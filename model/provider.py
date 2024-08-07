from django.db import models
from datetime import datetime, timedelta
from django.utils import timezone
import logging
# from .email_notification import Email_notification, send_notification
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
# f = Fernet.generate_key()

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


FTP_CHOICES = (
    ('FTP', 'FTP'),
    ('SFTP', 'SFTP')
)

PROVIDER_TYPE = (
    ('FTP', 'FTP'),
    ('API', 'API')
)
 

# providers model
class Providers(models.Model):
    official_name = models.CharField(max_length=64)
    working_name = models.CharField(max_length=64)
    in_production = models.BooleanField(default=True)
    provider_type = models.CharField(max_length=4, default='FTP', choices=PROVIDER_TYPE)
    source_schema = models.CharField(max_length=50, blank=True, null=True)
    delivery_method = models.CharField(max_length=50, blank=True, null=True, choices=DELIVERY_METHOD)
    article_switch = models.BooleanField(default=False)
    requirement_override = models.BooleanField(default=False)
    usda_source = models.BooleanField(default=False)
    archive_switch = models.BooleanField(default=False)
    minimum_delivery_fq = models.IntegerField(help_text="Enter frequency (number of days) when to sync the data with API", default=30)
    last_time_received = models.DateTimeField(auto_now=True, help_text="This will be auto field as and when the FTP will be accessed")
    status = models.CharField(max_length=10, default="success", 
                                        help_text="For the first time enter 'Initial'. This field will maintain last sync status success or failed"
                                        )
    last_error_message = models.TextField(null=True, 
                                          blank=True,
                                          help_text="In case of error last error message will be stored here. Don't enter anything here"
                                          )

    next_due_date = models.DateTimeField(null=True, 
                                         help_text="This will be filled automatically base on minimum_delivery_frequency. Don't enter anything here"
                                         )
    def __str__(self) -> str:
        return self.official_name
    
    # call save method to assign next due date
    def save(self, *args, **kwargs):
        self.next_due_date = datetime.now(tz=timezone.utc) + timedelta(self.minimum_delivery_fq)
        super(Providers, self).save(*args, **kwargs)


# Model to maintain history of access of API's and FTP's
class Fetch_history(models.Model):
    provider = models.ForeignKey(Providers, related_name='fetch_history', on_delete=models.DO_NOTHING)
    status = models.CharField(max_length=10, default='completed')
    error_message = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.provider.official_name + '->' + self.status


# Model to list all the FTP with attributes
class Provider_meta_data_FTP(models.Model):
    provider = models.ForeignKey(Providers, 
                                 related_name="ftp_provider", 
                                 on_delete=models.DO_NOTHING,
                                 help_text="Select Provider name"
                                 )
    server = models.TextField(help_text="Enter FTP address")
    protocol = models.CharField(max_length=10, choices=FTP_CHOICES, help_text="Enter Protocol used by this FTP. i.e. FTP / SFTP")
    site_path = models.TextField(default="/", help_text="Enter default location where file is stored on FTP server")

    is_password_required = models.BooleanField(default=True, help_text="Is this FTP password protected?")
    account = models.CharField(max_length=100, null=True, blank=True, 
                               help_text="Username to login to FTP. if is_password_required is selected this field is required"
                               )
    password = EncryptedField(null=True, blank=True, 
                              help_text="Password to login to FTP. if is_password_required is selected this field is required"
                              )

    pull_switch = models.CharField(max_length=50, null=True, blank=True)

    # email_notification = models.ForeignKey(Email_notification, 
    #                                        on_delete=models.DO_NOTHING, 
    #                                        blank=True, 
    #                                        null=True,
    #                                        help_text="In case email notifications are required to be sent to inform status, select the email group. This is optional"
    #                                        )

    # validations to the model fields.
    # These validations are applied based on the nature of the api's
    # some api's need paginated info, some required token, some are open etc.
    def clean(self):
        # if token is rquired on end points make site_token required
        if self.is_password_required and (self.account in (None, '') or self.password in (None, '')):
            raise ValidationError(
                {'error': "If password is required, please provide password"}
                )


    # method to return decrypted password
    @property
    def pswd(self):
        # return decrypt_data(self.password)
        return self.password


# Model to list all the API's with attributes
class Provider_meta_data_API(models.Model):
    provider = models.ForeignKey(Providers, 
                                 related_name="api_provider", 
                                 on_delete=models.DO_NOTHING,
                                 help_text="Select Provider name"
                                 )   
    api_meta_type = models.CharField(null=True, 
                                     blank=True, 
                                     max_length=20, 
                                     choices=API_TYPE,
                                     help_text="Select Type of API"
                                     ) 
    base_url = models.URLField(help_text="Enter Base URL of the API")

    identifier_type = models.CharField(max_length=50, 
                                       help_text="Enter Identifier type / name. For example 'usda funder id' "
                                       )
    identifier_code = models.CharField(max_length=50, 
                                       help_text="Enter Identifier code for example 100000199"
                                       )

    is_token_required = models.BooleanField(default=False, 
                                            help_text="If this API endpoint is password protected select the check box"
                                            )
    site_token = EncryptedField(null=True, 
                                blank=True, 
                                help_text="If 'is_token_required' is selected provide password / token for API"
                                )

    pull_switch = models.CharField(max_length=50, null=True, blank=True)

    # email_notification = models.ForeignKey(Email_notification, 
    #                                        on_delete=models.DO_NOTHING, 
    #                                        blank=True, 
    #                                        null=True,
    #                                        help_text="In case email notifications are required to be sent to inform status, select the email group. This is optional"
    #                                        )
    
    proxy_host_url = models.TextField(null=True, blank=True,
                                      help_text="Provide proxy hosts if any. This is optional"
                                      )
    external_library_url = models.TextField(null=True, blank=True,                                      
                                            help_text="Provide external library address if any. This is optional"
                                            )

    # this info is required in case of pagination is required on API's
    is_paginated = models.BooleanField(default=False,
                                        help_text="Is this api paginated? Select if yes. This is optional"
                                       )
    page_number = models.IntegerField(null=True, default=1,
                                    help_text="If paginated, enter the first page number. Default is 1"
                                      )

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
      

    # method to decrypt the token
    @property
    def pswd(self):
        # return decrypt_data(self.site_token)
        return self.site_token
