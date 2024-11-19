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

ARTICLE_PATH = settings.ARTICLE_ROOT
PROCESSED_ARTICLE = settings.PROCESSED_ARTICLE

# Class to remove the existing file.
# This will be used when we need to replace the existing file that is stored with the same name.

class OverWriteStorage(FileSystemStorage):
    def get_replace_or_create_file(self, name, max_length=None):
        if self.exists(name):
            os.remove(os.path.join(self.location, name))
            return super(OverWriteStorage, self).get_replace_or_create_file(name, max_length)


# Function to return the storage file path.
def get_invalid_file_path(instance, filename):
    return '{0}/{1}'.format('INVALID_FILES',filename)

def get_article_file_path(instance, filename):
    return '{0}/{1}/{2}'.format('ARTICLE', (instance.provider.working_name).replace(' ', '_') ,filename)


# model class to archive the error message that occures during processing / reading the xml/json file
class Unreadable_files(models.Model):
    source = models.TextField()
    file_type = models.CharField(max_length=10)
    file_content = models.FileField(upload_to=get_invalid_file_path, 
                                    storage=OverWriteStorage(),
                                    help_text="Browse the file"
                                )
    error_msg = models.TextField()
    date_stamp = models.DateTimeField(auto_now=True)



# article attribute model
class Article_attributes(models.Model):

    article_file = models.FileField(upload_to=get_article_file_path, 
                                    storage=OverWriteStorage(), 
                                    help_text="Browse the file"
                                    )
    
    journal = models.FileField(blank=True, 
                               null=True, 
                               help_text="This field value will assigned automatically with the value assigned in article_file"
                               )

    title = models.TextField(blank=True, null=True, help_text="Article title")
    type_of_record = models.CharField(max_length=24, choices=RECORD_CHOICES, help_text="Select from drop down")
    provider = models.ForeignKey(Providers, related_name="provider", on_delete=models.DO_NOTHING)
    archive = models.ForeignKey(Archive, related_name="archives", on_delete=models.DO_NOTHING)
    last_step = models.IntegerField(default=2, help_text="Last stage article passed through 1-11")
    last_status = models.CharField(default="active", max_length=10, choices=STATUS, help_text="Select from drop down")
    note = models.TextField(default="ok", help_text="Note, warning or error note")
    DOI = models.TextField(null=True, blank=True, help_text="A unique and persistent identifier")
    PID = models.TextField(null=True, blank=True, help_text="A locally assign identifier")
    MMSID = models.TextField(null=True, blank=True, help_text="The article's Alma identifer")
    provider_rec = models.CharField(max_length=10,null=True, blank=True, help_text="Provider article identifier")
    start_date = models.DateTimeField(auto_now=True, help_text="The date the article object was created")
    current_date = models.DateTimeField(auto_now_add=True, help_text="The date finished the last stage")
    end_date = models.DateTimeField(null=True, help_text="The data the article is staged for Alma")
    deposite_path = models.TextField(default=ARTICLE_PATH)
    is_content_changed = models.BooleanField(
                    default=False, 
                    help_text="Flag to maintain if the existing content is changed and file_content is updated")

    # def save(self, *args, **kwargs):
    #     if self.file_name_on_local_storage in ('', None):
    #         # article_file = journal
    #         self.journal = self.article_file
    #     super(Article_attributes, self).save(*args, **kwargs)



# Function to return the storage file path.
def get_json_file_path(instance, filename):
    return (settings.PROCESSED_ARTICLES + '\\' + filename)

# jsonified article attribute model
class Jsonified_articles(models.Model):

    article_file = models.FileField(upload_to=get_json_file_path, 
                                    storage=OverWriteStorage(), 
                                    help_text="Browse the file"
                                    )
    
    journal = models.FileField(blank=True, 
                               null=True, 
                               help_text="This field value will assigned automatically with the value assigned in article_file"
                               )

    title = models.TextField(blank=True, null=True, help_text="Article title")
    type_of_record = models.CharField(max_length=24, choices=RECORD_CHOICES, help_text="Select from drop down")
    article_attributes = models.ForeignKey(Article_attributes, related_name="article_attribute", on_delete=models.DO_NOTHING)
    last_step = models.IntegerField(default=3, help_text="Last stage article passed through 1-11")
    last_status = models.CharField(default="active", max_length=10, choices=STATUS, help_text="Select from drop down")
    note = models.TextField(default="ok", help_text="Note, warning or error note")
    DOI = models.TextField(null=True, blank=True, help_text="A unique and persistent identifier")
    PID = models.TextField(null=True, blank=True, help_text="A locally assign identifier")
    MMSID = models.TextField(null=True, blank=True, help_text="The article's Alma identifer")
    provider_rec = models.CharField(max_length=10,null=True, blank=True, help_text="Provider article identifier")
    start_date = models.DateTimeField(auto_now=True, help_text="The date the article object was created")
    current_date = models.DateTimeField(auto_now_add=True, help_text="The date finished the last stage")
    end_date = models.DateTimeField(null=True, help_text="The data the article is staged for Alma")
    deposite_path = models.TextField(default=PROCESSED_ARTICLE)

