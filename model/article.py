from django.db import models
from django.core.files.storage import FileSystemStorage
from .provider import Providers
from .archive import Archive
import os
from django.conf import settings
from model.journal import Journal
from django.db.models.signals import post_save
from django.dispatch import receiver

# record type options for article table
RECORD_CHOICES = (
    ('article', 'article'),
    ('retraction', 'retraction'),
    ('letter to the editor','letter to the editor')
)

# status options for article table
STATUS = (
    ('active','active'),
    ('dropped','dropped'),
    ('completed', 'completed')
)

ARTICLE_PATH = settings.ARTICLE_ROOT

# Class to remove the existing file.
# This will be used when we need to replace the existing file that is stored with the same name.

class OverWriteStorage(FileSystemStorage):
    def get_replace_or_create_file(self, name, max_length=None):
        if self.exists(name):
            os.remove(os.path.join(self.location, name))
            return super(OverWriteStorage, self).get_replace_or_create_file(name, max_length)


# Function to return the storage file path.
def get_invalid_file_path(instance, filename):
    return '{0}/{1}'.format('INVALID_FILES', filename)


def get_article_file_path(instance, filename):
    if not instance.id:
        instance.save()
    extension = filename.split('.')[-1]
    filename = str(instance.id) + '.' + extension
    return '{0}/{1}/{2}'.format(
        'ARTICLES',
        (instance.provider.working_name).replace(' ','_'),
        filename
        )


def get_pickel_file_path(instance, filename):
    return '{0}/{1}/{2}'.format('ARTICLE_CITATION', (instance.provider.working_name).replace(' ', '_'), filename)


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



# article attribute model Article_attributes
class Article(models.Model):


    article_file = models.FileField(upload_to=get_article_file_path, 
                                    blank=True, null=True,
                                    storage=OverWriteStorage(), 
                                    help_text="Browse the file"
                                    )
    
    journal = models.ForeignKey(Journal, 
                                related_name="article_journal", 
                                on_delete=models.SET_NULL, 
                                blank=True, null=True
                                )

    title = models.TextField(blank=True, null=True, help_text="Article title")
    type_of_record = models.CharField(max_length=24, choices=RECORD_CHOICES, help_text="Select from drop down")
    provider = models.ForeignKey(Providers, related_name="provider", on_delete=models.DO_NOTHING)
    archive = models.ForeignKey(Archive, related_name="archives", on_delete=models.DO_NOTHING)
    last_step = models.IntegerField(default=2, help_text="Last stage article passed through 1-11")
    last_status = models.CharField(default="active", max_length=10, choices=STATUS, help_text="Select from drop down")
    note = models.TextField(default='none', help_text="Note, Warning or Error msg")
    DOI = models.TextField(null=True, blank=True, help_text="A unique and persistent identifier")
    PID = models.TextField(null=True, blank=True, help_text="A locally assign identifier")
    MMSID = models.TextField(null=True, blank=True, help_text="The article's Alma identifier")
    provider_rec = models.TextField(null=True, blank=True, help_text="Provider article identifier")
    start_date = models.DateTimeField(auto_now=True, help_text="The date the article object was created")
    current_date = models.DateTimeField(auto_now_add=True, help_text="The date finished the last stage")
    end_date = models.DateTimeField(null=True, help_text="The data the article is staged for Alma")
    citation_pickle = models.FileField(upload_to=get_pickel_file_path,
                                       storage=OverWriteStorage(), 
                                       help_text="This field will store citation article in pickle format as .pkl or .pickle file extension"
                                       )
    import_type = models.CharField(blank=True, null=True, default=None, max_length=16)



# This table will be used to archive number of processed records
class ProcessedArticleHistory(models.Model):
    new_usda_record_processed = models.BigIntegerField(default=0)
    merge_usda_record_processed = models.BigIntegerField(default=0)
    new_publisher_record_processed = models.BigIntegerField(default=0)
    merge_publisher_record_processed = models.BigIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)