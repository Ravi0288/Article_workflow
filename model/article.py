from django.db import models
from django.core.files.storage import FileSystemStorage
from .provider import Providers
from .archive import Archive
import os
from django.conf import settings

# record type options for article table
RECORD_CHOICES = (
    ('article', 'article'),
    ('retraction', 'retraction'),
    ('letter to the editor','letter to the editor')
)

# status options for article table
STATUS = (
    ('active','active'),
    ('failed','failed'),
    ('completed', 'completed')
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
def get_file_path(instance, filename):
    return filename

# model class to archive the error message that occures during processing / reading the xml file
class Unreadable_xml_files(models.Model):
    file_name = models.CharField(max_length=100)
    error_msg = models.TextField()



# article attribute model
class Article_attributes(models.Model):

    article_file = models.FileField(upload_to=get_file_path, 
                                    storage=OverWriteStorage(), 
                                    help_text="Browse the file"
                                    )
    
    journal = models.FileField(blank=True, 
                               null=True, 
                               help_text="This field value will assigned automatically with the value assigned in article_file"
                               )

    title = models.TextField(blank=True, null=True, help_text="Article title")
    type_of_record = models.CharField(max_length=24, choices=RECORD_CHOICES, help_text="Select from drop down")
    provider = models.ForeignKey(Providers, related_name="provsider", on_delete=models.DO_NOTHING)
    archive = models.ForeignKey(Archive, related_name="archives", on_delete=models.DO_NOTHING)
    last_step = models.IntegerField(default=2, help_text="Last stage article passed through 1-11")
    last_status = models.CharField(default="active", max_length=10, choices=STATUS, help_text="Select from drop down")
    note = models.TextField(default="ok", help_text="Note, warning or error note")
    DOI = models.TextField(null=True, blank=True, help_text="A unique and persistent identifier")
    PID = models.TextField(null=True, blank=True, help_text="A locally assign identifie")
    MMSID = models.TextField(null=True, blank=True, help_text="The article's Alma identifer")
    provider_rec = models.CharField(max_length=10,null=True, blank=True, help_text="Provider article identifier")
    start_date = models.DateTimeField(auto_now=True, help_text="The date the article object was created")
    current_date = models.DateTimeField(auto_now_add=True, help_text="The date finished the last stage")
    end_date = models.DateTimeField(null=True, help_text="The data the article is staged for Alma")
    deposite_path = models.TextField(default=ARCHIVE_PATH)


    def save(self, *args, **kwargs):
        if self.file_name_on_local_storage in ('', None):
            # article_file = journal
            self.journal = self.article_file
        super(Article_attributes, self).save(*args, **kwargs)