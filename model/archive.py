from django.db import models
from django.core.files.storage import FileSystemStorage
from .provider import Providers
import os
from django.conf import settings

# choices to be used for status of article attributs
CHOICES= (
    ('completed', 'completed'),
    ('waiting', 'waiting'),
    ('processed','processed'),
    ('failed', 'failed')
)

RECORD_CHOICES = (
    ('article', 'article'),
    ('retraction', 'retraction'),
    ('letter to the editor','letter to the editor')
)

ARCHIVE_PATH = settings.MEDIA_ROOT

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
    extenstion = filename.split('.')[-1]
    filename = str(instance.id) + '.' + extenstion
    return '{0}/{1}'.format(
        instance.provider.official_name,
        filename
        )


# Model to store downloaded files/folders from FTP/SFTP's
class Archive(models.Model):
    provider = models.ForeignKey(Providers, 
        on_delete=models.DO_NOTHING, 
        related_name="archives",
        help_text="Select provider"
        )

    file_content = models.FileField( upload_to=get_file_path, 
                                    blank=True, null=True, 
                                    storage=OverWriteStorage(),
                                    help_text="Browse the file"
                                )
    
    file_name_on_source = models.CharField(max_length=500, 
                                           null=True, blank=True, 
                                           help_text="File name for FTP will be assigned automatically as received. For API \
                                            No file name is received hence file name will be saved as DOI.json"
                                           )
    file_name_on_local_storage = models.CharField(max_length=500, 
                                                  null=True, blank=True, 
                                                  help_text="File name will be assigned automatically as id.extesion"
                                                  )
    file_size = models.IntegerField(default=0, 
                                    help_text="File size will be assigned automatically"
                                    )
    file_type = models.CharField(max_length=20, 
                                 help_text="File type will be assigned automatically"
                                 )

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
    deposite_path = models.TextChoices(null=True, blank=True, default=ARCHIVE_PATH)
    def __str__(self) -> str:
        return 'File Name on Source :' + self.file_name_on_source + ', Local Storage File name :' + self.file_name_on_local_storage
    

    def save(self, *args, **kwargs):
        if self.file_name_on_local_storage in ('', None):
            # assign default file name as the id.extesnsion_of_the_received_file
            self.file_name_on_local_storage = str(self.id) + self.file_name_on_source.split('.')[-1]
        super(Archive, self).save(*args, **kwargs)