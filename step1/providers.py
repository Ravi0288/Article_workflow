from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.signals import request_finished
from rest_framework.viewsets import ModelViewSet
from rest_framework import serializers
from datetime import datetime, timedelta
import logging
from .email_notification import Email_notification, send_comment_mail_notification
from cryptography.fernet import Fernet
from django.core.exceptions import ValidationError
from django.conf import settings
from configurations.common import EncryptedField

# record log
logger = logging.getLogger(__name__)

# key is generated 
# key = Fernet.generate_key() 
  
# value of key is assigned to a variable 
# f = Fernet(key) 
f = Fernet(settings.FERNET_KEY)

# function to encrypt data
def encrypt_data(data):
    encrypted_data = f.encrypt(data.encode())
    return encrypted_data

# function to decrypt encrypted data
def decrypt_data(encrypted_data):
    return f.decrypt(encrypted_data).decode()

# update password
def update_password(old_password, new_password):
    password = decrypt_data(old_password)
    new_password = decrypt_data(new_password)
    if not((password == new_password) and (new_password in ('', None, ' '))):
        password = new_password
    return encrypt_data(password)

# choices to be used for status of article attributs
CHOICES= (
    ('waiting', 'waiting'),
    ('processed','processed'),
    ('failed', 'failed')
)

# delivery method choices
DELIVERY_METHOD = (
    ('deposit','deposit'),
    ('FTP','FTP'),
    ('SFTP','SFTP'),
    ('API','API')
)

API_TYPE = (
    ('Chorus', 'Chorus'),
    ('CrossRef', 'CrossRef'),
    ('Submission','Submission')
)

# providers model
class Provider_model(models.Model):
    official_name = models.CharField(max_length=100)
    working_name = models.CharField(max_length=50)
    in_production = models.BooleanField(max_length=15)
    archive_switch = models.BooleanField(max_length=15)
    article_switch = models.BooleanField(max_length=15)
    requirement_override = models.BooleanField(max_length=15)

    def __str__(self) -> str:
        return self.official_name

# Model to maintain history of access of API's and FTP's
class Fetch_history(models.Model):
    provider = models.ForeignKey(Provider_model, related_name='fetch_history', on_delete=models.DO_NOTHING)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, default='success')
    error_message = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.provider.official_name + '->' + self.status


# Model to list all the FTP with attributes
class Provider_meta_data_FTP(models.Model):
    provider = models.ForeignKey(Provider_model, related_name="ftp_provider", on_delete=models.CASCADE)
    server = models.TextField()
    protocol = models.CharField(max_length=10)
    site_path = models.CharField(max_length=50)
    account = models.CharField(max_length=50)
    password = EncryptedField(null=True, blank=True)
    minimum_delivery_fq = models.IntegerField()
    last_pull_time = models.DateTimeField(auto_now=True)
    pull_switch = models.BooleanField()
    last_pull_status = models.CharField(max_length=10, default="success")
    last_error_message = models.TextField(null=True, blank=True)
    next_due_date = models.DateTimeField(null=True)

    # call save method to assign next due date
    def save(self, *args, **kwargs):
        self.next_due_date = datetime.now() + timedelta(self.minimum_delivery_fq)
        super(Provider_meta_data_FTP, self).save(*args, **kwargs)

    # method to return decrypted password
    @property
    def pswd(self):
        # return decrypt_data(self.password)
        return self.password


# Model to list all the API's with attributes
class Provider_meta_data_API(models.Model):
    api_meta_type = models.CharField(null=True, blank=True, max_length=20, choices=API_TYPE)
    provider = models.ForeignKey(Provider_model, related_name="api_provider", on_delete=models.CASCADE)    
    base_url = models.URLField()
    identifier_code = models.CharField(max_length=50)
    identifier_type = models.CharField(max_length=50)
    last_pull_time = models.DateTimeField(auto_now=True)
    api_switch = models.BooleanField()

    is_token_required = models.BooleanField(default=False)
    site_token = EncryptedField(null=True, blank=True)

    minimum_delivery_fq = models.IntegerField()
    last_pull_status = models.CharField(max_length=10, default="success")
    last_error_message = models.TextField(null=True, blank=True)
    next_due_date = models.DateTimeField(null=True)
    email_notification = models.ForeignKey(Email_notification, on_delete=models.DO_NOTHING, blank=True, null=True)
    proxy_host_url = models.TextField(null=True)
    external_library_url = models.TextField(null=True)

    # this info is required in case of pagination is required on API's
    is_paginated = models.BooleanField(default=False)
    page_number = models.IntegerField(null=True)
    last_accessed_page = models.IntegerField(null=True)

    # validations to the model fields.
    # These validations are applied based on the nature of the api's
    # some api's need paginated info, some required token, some are open etc.
    def clean(self):
        # if pagination is rquired on end points make page_number required
        if self.is_paginated and self.page_number == None:
            raise ValidationError(
                {'error': "If pagination is True, page_number  is required."}
                )
        
        # if token is rquired on end points make site_token required
        if self.is_token_required and self.site_token in (None, ''):
            raise ValidationError(
                {'error': "If token is required, please provide site token."}
                )

    # call default save method to encrypt token and assign next due date
    def save(self, *args, **kwargs):
        self.next_due_date = datetime.now() + timedelta(self.minimum_delivery_fq)
        super(Provider_meta_data_API, self).save(*args, **kwargs)        

    # method to decrypt the token
    @property
    def pswd(self):
        # return decrypt_data(self.site_token)
        return self.site_token


# serializers to models
class Provider_model_serializer(serializers.ModelSerializer):
    class Meta:
        model = Provider_model
        fields = '__all__'

class Fetch_history_serializer(serializers.ModelSerializer):
    class Meta:
        model = Fetch_history
        fields = '__all__'


class Provider_meta_data_FTP_serializer(serializers.ModelSerializer):
    class Meta:
        model = Provider_meta_data_FTP
        fields = '__all__'
        # exclude = ('password',)


class Provider_meta_data_API_serializer(serializers.ModelSerializer):
    class Meta:
        model = Provider_meta_data_API
        fields = '__all__'
        # exclude = ('site_token',)
    
    # validations method clean implementaion
    def validate(self, attrs):
        instance = Provider_meta_data_API(**attrs)
        instance.clean()
        return attrs


# viewsets to models
class Provider_viewset(ModelViewSet):
    queryset = Provider_model.objects.all()
    serializer_class = Provider_model_serializer


class Fetch_history_viewset(ModelViewSet):
    queryset = Fetch_history.objects.all()
    serializer_class = Fetch_history_serializer

class Provider_meta_data_FTP_viewset(ModelViewSet):
    queryset = Provider_meta_data_FTP.objects.all()
    serializer_class = Provider_meta_data_FTP_serializer

class Provider_meta_data_API_viewset(ModelViewSet):
    queryset = Provider_meta_data_API.objects.all()
    serializer_class = Provider_meta_data_API_serializer



# triggers to update fetch history. This function to be called automatically to update history of each accesss to FTP's
@receiver(post_save, sender=Provider_meta_data_FTP)
def update_history_for_FTP(sender, instance, created, **kwargs):
    # if record is updated
    if not created:
        # create fetch_history for log purposes
        Fetch_history.objects.create(
            provider = instance.provider,
            status = instance.last_pull_status,
            error_message = instance.last_error_message
        )
        return True


# triggers to update fetch history. This function to be called automatically to update history of each accesss to API's
@receiver(post_save, sender=Provider_meta_data_API)
def update_history_for_API(sender, instance, created, **kwargs):
    # if record is updated
    if not created:
        # create fetch_history for log purposes
        Fetch_history.objects.create(
            provider = instance.provider,
            status = instance.last_pull_status,
            error_message = instance.last_error_message
        )

        # if api is failed send the email.
        if instance.status == 'failed':
            # send_comment_mail_notification(instance)
            pass
            
        return True