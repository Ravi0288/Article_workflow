from django.db import models
from django.core.files.storage import FileSystemStorage
import os
from rest_framework.viewsets import ModelViewSet
from rest_framework.serializers import ModelSerializer
from datetime import datetime

from nal_library_conf.settings import UPLOAD_ROOT
from rest_framework.decorators import api_view


# choices to be used for status of article attributs
CHOICES= (
    ('waiting', 'waiting'),
    ('processed','processed'),
    ('failed', 'failed')
)


# Class to remove the existing file.
# This will be used when we need to replace the existing file that is stored with the same name.

class OverWriteStorage(FileSystemStorage):
    def get_replace_or_create_file(self, name, max_length=None):
        if self.exists(name):
            os.remove(os.path.join(self.location, name))
            return super(OverWriteStorage, self).get_replace_or_create_file(name, max_length)


upload_storage = FileSystemStorage(location=UPLOAD_ROOT, base_url='/uploads')

# Function to return the storage file path.
# This function will return file path as article_library/Current_year/Current_month/day/file_name_with_extension
# Any downloaded file will be stored like this.
# http://localhost:8000/article_library/2024/2/8/resume.pdf
        
def get_file_path(instance, filename):
    return '{0}/{1}/{2}/{3}'.format(
        datetime.today().year, 
        datetime.today().month,
        datetime.today().day, 
        filename
        )


# Model to record logs of downloaded files/folders from FTP/SFTP's
class Archived_article_attribute(models.Model):
    provider = models.URLField()
    file_content = models.FileField(upload_to=get_file_path, blank=True, null=True, storage=OverWriteStorage())
    file_name_on_ftp = models.CharField(max_length=500)
    file_size = models.BigIntegerField(default=0)
    file_type = models.CharField(max_length=20)
    received_on = models.DateTimeField(auto_now_add=True)
    processed_on = models.DateTimeField(null=True)
    status = models.CharField(max_length=12, choices=CHOICES)
    notes = models.TextField(default="N/A")


    def __str__(self) -> str:
        return self.provider
    

# serializer for Archived_article_attribute model
class Archived_article_attribute_serializers(ModelSerializer):
    class Meta:
        model = Archived_article_attribute
        fields = '__all__'


# views for Archived_article_attribute
class Archived_article_attribute_view(ModelViewSet):
    queryset = Archived_article_attribute.objects.all()
    serializer_class = Archived_article_attribute_serializers



