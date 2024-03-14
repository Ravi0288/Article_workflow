from django.db import models
from rest_framework.viewsets import ModelViewSet
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from datetime import datetime, timedelta
import logging
logger = logging.getLogger(__name__)
from django.conf import settings

from cryptography.fernet import Fernet

# key is generated 
key = Fernet.generate_key() 
  
# value of key is assigned to a variable 
f = Fernet(key) 

# function to encrypt data
def encrypt_data(data):
    encrypted_data = f.encrypt(data.encode())
    return encrypted_data

# function to decrypt encrypted data
def decrypt_data(encrypted_data):
    decrypted_data = f.decrypt(encrypted_data).decode()
    return decrypted_data

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

# delivery model
class Provider_model(models.Model):
    official_name = models.CharField(max_length=100)
    working_name = models.CharField(max_length=50)
    in_production = models.BooleanField(max_length=15)
    archive_switch = models.BooleanField(max_length=15)
    article_switch = models.BooleanField(max_length=15)
    requirement_override = models.BooleanField(max_length=15)

    def __str__(self) -> str:
        return self.official_name


class Provider_meta_data_FTP(models.Model):
    provider = models.ForeignKey(Provider_model, related_name="ftp_provider", on_delete=models.CASCADE)
    server = models.TextField()
    protocol = models.CharField(max_length=10)
    site_path = models.CharField(max_length=50)
    account = models.CharField(max_length=50)
    password = models.TextField()
    minimum_delivery_fq = models.IntegerField()
    last_pull_time = models.DateTimeField(auto_now=True)
    pull_switch = models.BooleanField()
    last_pull_status = models.CharField(max_length=10, default="pass")
    next_due_date = models.DateTimeField(null=True)

    def save(self, *args, **kwargs):
        self.password = encrypt_data(self.password)
        self.next_due_date = datetime.today() + timedelta(self.minimum_delivery_fq)
        super(Provider_meta_data_FTP, self).save(*args, **kwargs)

    @property
    def pswd(self):
        return decrypt_data(self.password)


class Provider_meta_data_API(models.Model):
    provider = models.ForeignKey(Provider_model, related_name="api_provider", on_delete=models.CASCADE)    
    base_url = models.URLField()
    identifier_code = models.CharField(max_length=50)
    identifier_type = models.CharField(max_length=50)
    last_pull_time = models.DateTimeField(auto_now=True)
    api_switch = models.BooleanField()
    site_token = models.TextField()
    minimum_delivery_fq = models.IntegerField()
    last_pull_status = models.CharField(max_length=10, default="pass")
    next_due_date = models.DateTimeField(null=True)

    def save(self, *args, **kwargs):
        self.site_token = encrypt_data(self.site_token)
        self.next_due_date = datetime.today() + timedelta(self.minimum_delivery_fq)
        super(Provider_meta_data_API, self).save(*args, **kwargs)        

    @property
    def pswd(self):
        return decrypt_data(self.site_token)

class Provider_model_serializer(serializers.ModelSerializer):
    class Meta:
        model = Provider_model
        fields = '__all__'


class Provider_meta_data_FTP_serializer(serializers.ModelSerializer):
    class Meta:
        model = Provider_meta_data_FTP
        fields = '__all__'


class Provider_meta_data_API_serializer(serializers.ModelSerializer):
    class Meta:
        model = Provider_meta_data_API
        fields = '__all__'


class Provider_viewset(ModelViewSet):
    queryset = Provider_model.objects.all()
    serializer_class = Provider_model_serializer

class Provider_meta_data_FTP_viewset(ModelViewSet):
    queryset = Provider_meta_data_FTP.objects.all()
    serializer_class = Provider_meta_data_FTP_serializer

class Provider_meta_data_API_viewset(ModelViewSet):
    queryset = Provider_meta_data_API.objects.all()
    serializer_class = Provider_meta_data_API_serializer






    

