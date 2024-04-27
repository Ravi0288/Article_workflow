from django.db import models

from step1.archive_article import Archived_article
from step1.providers import Providers
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view
from rest_framework.response import Response
import zipfile
import xmltodict
import re
import os
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.core.files.base import ContentFile
import json
import pytz
import datetime
import shutil


RECORD_CHOICES = (
    ('article', 'article'),
    ('retraction', 'retraction'),
    ('letter to the editor','letter to the editor')
)

STATUS = (
    ('active','active'),
    ('failed','failed'),
    ('completed', 'completed')
)


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


class Article_attributes(models.Model):
    article_file = models.FileField(upload_to=get_file_path, storage=OverWriteStorage(), help_text="Browse the file")
    title = models.TextField(blank=True, null=True, help_text="Article title")
    type_of_record = models.CharField(max_length=24, choices=RECORD_CHOICES, help_text="Select from drop down")
    # journal = models.ForeignKey(Providers, related_name="journals", on_delete=models.CASCADE)
    provider = models.ForeignKey(Providers, related_name="provsider", on_delete=models.CASCADE)
    archive = models.ForeignKey(Archived_article, related_name="archives", on_delete=models.CASCADE)
    last_stage = models.IntegerField(default=2, help_text="Last stage article passed through 1-11")
    last_status = models.CharField(default="active", max_length=10, choices=STATUS, help_text="Select from drop down")
    note = models.TextField(default="ok", help_text="Note, warning or error note")
    DOI = models.TextField(null=True, blank=True, help_text="A unique and persistent identifier")
    PID = models.TextField(null=True, blank=True, help_text="A locally assign identifie")
    MMSID = models.TextField(null=True, blank=True, help_text="The article's Alma identifer")
    provider_rec = models.CharField(max_length=10,null=True, blank=True, help_text="Provider article identifier")
    start_date = models.DateTimeField(auto_now=True, help_text="The date the article object was created")
    current_date = models.DateTimeField(auto_now_add=True, help_text="The date finished the last stage")
    end_date = models.DateTimeField(null=True, help_text="The data the article is staged for Alma")


class Article_attributes_serializer(ModelSerializer):
    class Meta:
        model = Article_attributes
        fields = '__all__'


class Article_attributes_viewset(ModelViewSet):
    queryset = Article_attributes.objects.all()
    serializer_class = Article_attributes_serializer




# update archive artile flags if processed
def update_archive_article(row):
    row.is_processed = True
    row.processed_on = datetime.datetime.now(tz=pytz.utc)
    row.save()

# function to check if there is any zipped folder inside any directory or subdirectory
def is_any_zipped_remains(source):
    # Traverse the directory tree
    for root, dirs, files in os.walk(source):
        # Check if any file in the current directory or its subdirectories is zipped
        for file_name in files:
            if file_name.endswith('.zip'):
                return True
    # If no zip file is found in any subfolder
    return False


# find title of the json content
def find_title(json_obj):
    for key, value in json_obj.items():
        # Check if the key is a potential title candidate
        if key.lower() == 'title':
            # Assume the title is a string value
            if isinstance(value, str):
                return value
            # If the value is another dictionary, recursively search for the title
            elif isinstance(value, dict):
                nested_title = find_title(value)
                if nested_title:
                    return nested_title

    # If no title is found
    return None



# create new objects
def create_new_object(source, row):
    # changing the default settings base directory root
    settings.MEDIA_ROOT = settings.BASE_DIR / 'ARTICLES'
    try:
        qs = Article_attributes()
        qs.type_of_record = 'article'
        qs.provider = row.provider
        qs.archive = row
        qs.last_stage = 2
        qs.last_status = 'completed'
        qs.note = "success"
        qs.DOI = row.unique_key
        qs.PID = "A locally assign identifie"
        qs.MMSID = "The article's Alma identifer"
        qs.provider_rec = "indentf"

        x = source.replace('ARCHIVE_ARTICLE/','')
        x = x.replace('TEMP/','')
        with open(source, 'rb') as f:
            file_content = json.load(f)
            qs.title = find_title(file_content)
            f.seek(0)
            qs.article_file.save(x, ContentFile(f.read()))

        return True

    except Exception as e:
        Article_attributes.objects.create(
            title = "Error occured for Archive Article id number" + str(row.id) + 'and file path :' + row.file_content.name,
            type_of_record = 'N/A',
            provider = row.provider,
            archive = row,
            last_stage = 2,
            last_status = 'failed',
            note = e,
            DOI = row.unique_key,
            PID = "A locally assign identifie",
            MMSID = "The article's Alma identifer",
            provider_rec = "identifier"   
        )
        return False


# function to check if there is any zipped folder inside any directory or subdirectory
def is_any_zipped_remains(source):
    # Traverse the directory tree
    for root, dirs, files in os.walk(source):
        # Check if any file in the current directory or its subdirectories is zipped
        for file_name in files:
            if file_name.endswith('.zip'):
                return True
    # If no zip file is found in any subfolder
    return False


# Function to unzip
def unzip_file(source, destination, row):
    try:
        with zipfile.ZipFile(source, 'r') as zip_ref:
            zip_ref.extractall(destination)
        zip_ref.close()

        for root, dirs, files in os.walk(destination):
            for file_name in files:
                new_source = os.path.join(root, file_name)
                if not file_name.endswith('.xml'):
                    # some folders have got files other than xml format.
                    if file_name.endswith('.json'):
                        # if json file found create record
                        create_new_object(new_source, row)
                        os.remove(new_source)
                    elif not file_name.endswith('.json'):
                        print(file_name, "is not of xml type. If know file new action may be implemented here")
                        # removing the file that is not xml or json
                        os.remove(new_source)
                else:
                    # if xml file found jsonify it and than create new records
                    jsonify_file_content(new_source, row)

        return True

    except zipfile.BadZipFile:
        # Handle the case where the file is not a valid ZIP file
        # os.remove(source)
        print("zipped file cant be unzipped. it is corrupt or unsupported zipped file", source)
        pass
    except Exception as e:
        # Handle any other unexpected exceptions
        print("exception occured", e)
        pass
    return False


def jsonify_file_content(source, row):
    # some file got the wrong xml format, 
    # hence caused to stop the execution. Using try except to ignore the error due to corrupted xml files
    try:
        # open file
        with open(file=source, mode='rb') as xml_txt:                 
            # replace special character
            xml_txt = xml_txt.read().replace(
                b'&#x2018;', b'"').replace(
                    b'&#8216;',b'"').replace(
                        b'&lsquo;',b'"').replace(
                            b'&', b'&amp;')
            # xml_txt = preprocess_xml(xml_txt)
            json_data = xmltodict.parse(xml_txt, encoding='utf-8')

        # read the xml file and save as json to the same path
        json_file_name = source[:-4] + '.json'
        with open(json_file_name, "w") as f:
            json.dump(json_data, f)
        f.close()

        # make entry in tables
        create_new_object(json_file_name, row)

        # remove the xml file
        os.remove(source)
        return True
    
    except Exception as e:
        print("exception occured while jsonifying the xml content", e)
        return False


@api_view(['GET'])
def migrate_to_step2(request):
    qs = Archived_article.objects.filter(is_processed=False)
    for row in qs:
        source = 'ARCHIVE_ARTICLE/' + row.file_content.name
        destination = 'TEMP/' + source[:-4]
        if row.file_type in ('.zip', '.ZIP'):
            if unzip_file(source, destination, row):
                update_archive_article(row)
        elif row.file_type == '.json':
            if create_new_object(source, row):
                update_archive_article(row)
        elif row.file_type == '.xml':
            if jsonify_file_content(source, row):
                update_archive_article(row)
        else:
            print("unsupported file type found", source)

    shutil.rmtree('TEMP/')
    return Response("executed succcessfully")