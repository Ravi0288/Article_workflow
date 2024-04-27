from django.db import models
from django.core.files.storage import FileSystemStorage
import os
from rest_framework.viewsets import ModelViewSet
from rest_framework.serializers import ModelSerializer
from datetime import datetime
from .providers import Providers

from rest_framework.decorators import api_view


# choices to be used for status of article attributs
CHOICES= (
    ('success', 'success'),
    ('waiting', 'waiting'),
    ('processed','processed'),
    ('failed', 'failed')
)

RECORD_CHOICES = (
    ('article', 'article'),
    ('retraction', 'retraction'),
    ('letter to the editor','letter to the editor')
)

# Class to remove the existing file.
# This will be used when we need to replace the existing file that is stored with the same name.

class OverWriteStorage(FileSystemStorage):
    def get_replace_or_create_file(self, name, max_length=None):
        if self.exists(name):
            os.remove(os.path.join(self.location, name))
            return super(OverWriteStorage, self).get_replace_or_create_file(name, max_length)


# Function to return the storage file path.
# This function will return file path as article_library/Current_year/Current_month/day/file_name_with_extension

def get_file_path(instance, filename):
    return '{0}/{1}'.format(
        instance.provider.official_name,
        filename
        )


# Model to record logs of downloaded files/folders from FTP/SFTP's
class Archived_article(models.Model):
    provider = models.ForeignKey(Providers, 
        on_delete=models.CASCADE, 
        related_name="archives",
        help_text="Select provider"
        )

    file_content = models.FileField( upload_to=get_file_path, 
                                    blank=True, null=True, 
                                    storage=OverWriteStorage(),
                                    help_text="Browse the file"
                                )
    
    file_name_on_source = models.CharField(max_length=500, help_text="File name will be stored automatically")
    file_size = models.IntegerField(default=0, help_text="File size will be stored automatically")
    file_type = models.CharField(max_length=20, help_text="File type will be stored automatically")

    unique_key = models.CharField(max_length=500, 
                                  blank=True, null=True,
                                  help_text="Unique key to identify this record uniquely. Indentifier code or DOI etc"
                                  )

    received_on = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=12, 
                              choices=CHOICES, 
                              help_text="Last access status"
                            )

    is_processed = models.BooleanField(default=False, 
                                       help_text="Flag to maintain if the record is processed for step 2"
                                    )
    processed_on = models.DateTimeField(null=True)

    is_content_changed = models.BooleanField(
                    default=False, 
                    help_text="Flag to maintain if the existing content is changed and file_content is update"
                    )

    def __str__(self) -> str:
        return self.file_name_on_source
    

# serializer for Archived_article model
class Archived_article_serializers(ModelSerializer):
    class Meta:
        model = Archived_article
        fields = '__all__'


# views for Archived_article
class Archived_article_view(ModelViewSet):
    queryset = Archived_article.objects.all().order_by("-id")[:10]
    serializer_class = Archived_article_serializers



