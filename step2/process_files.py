from django.conf import settings
from step1.archive import Archive
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view
from rest_framework.response import Response
from model.article import Unreadable_xml_files, Article_attributes
from django.core.files.base import ContentFile
from .splitter import splitter

import pytz
import datetime
import shutil
import os
import zipfile


# unreadable xml file serializer
class Unreadable_xml_files_serializers(ModelSerializer):
    class Meta:
        model = Unreadable_xml_files
        fields = '__all__'

# unreadable xml file view sets
class Unreadable_xml_files_viewset(ModelViewSet):
    serializer_class = Unreadable_xml_files_serializers
    queryset = Unreadable_xml_files.objects.all()
    
    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.GET
        qs = qs.filter(**params.dict())
        return qs

# article attribute serializer
class Article_attributes_serializer(ModelSerializer):
    class Meta:
        model = Article_attributes
        fields = '__all__'


# article attribute viewset
class Article_attributes_viewset(ModelViewSet):
    queryset = Article_attributes.objects.all()
    serializer_class = Article_attributes_serializer

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.GET
        qs = qs.filter(**params.dict())
        return qs


# function to process xml/json files
def process_file(row, source):
    with open(source, 'r') as f:
        content = f.read()
        f.close()
    result, message = splitter(content)
    if message == 'successful':
        if len(result) > 1:
            for index, value in enumerate(result):
                if row.file_content.name.endswith('.json'):
                    file_name = row.file_content.name[:-5] + '_' + str(index+1) + '.json'
                else:
                    file_name = row.file_content.name[:-4] + '_' + str(index+1) + '.xml'

                create_new_object(file_name, row, 'success')
    else:
        invalid_xml_destination = os.path.join(settings.BASE_DIR, 'INVALID_XML_FILES')
        dest = shutil.copy(source, invalid_xml_destination)
        Unreadable_xml_files.objects.create(
            file_name = dest,
            error_msg = message
        )




# update archive artile flags if processed
def update_archive(row):
    row.status = "processed"
    row.processed_on = datetime.datetime.now(tz=pytz.utc)
    row.save()


# create new objects in article table
def create_new_object(source, row, note):
    # changing the default settings base directory root
    settings.MEDIA_ROOT = settings.BASE_DIR / 'ARTICLES'
    try:
        # create new record
        qs = Article_attributes()
        qs.type_of_record = 'article'
        qs.provider = row.provider
        qs.archive = row
        qs.last_step = 2
        qs.last_status = 'completed'
        qs.note = note
        qs.PID = "A locally assign identifier"
        qs.MMSID = "The article's Alma identifier"
        qs.provider_rec = "indentfier"

        x = source.replace('ARCHIVE/','')
        x = x.replace('TEMP/','')
        with open(source, 'rb') as f:
            f.seek(0)
            qs.article_file.save(x, ContentFile(f.read()))

        return True

    except Exception as e:
        # if exception occures create new record with status as failed
        Article_attributes.objects.create(
            title = "Error occured for Archive Article id number  " + str(row.id) + " and file path : " + row.file_content.name,
            type_of_record = 'N/A',
            provider = row.provider,
            archive = row,
            last_step = 2,
            last_status = 'failed',
            note = e,
            PID = "A locally assign identifie",
            MMSID = "The article's Alma identifer",
            provider_rec = "identifier"   
        )
        return False


# Function to unzip
# This function will iterate through each directory / subdirectory of archive and will find the .zip / .ZIP file.
# if file found the function will unzip the content to the same path under articles directory
def unzip_file(source, destination, row):
    try:
        # unzip the source file to destination path
        with zipfile.ZipFile(source, 'r') as zip_ref:
            zip_ref.extractall(destination)
        zip_ref.close()

    except zipfile.BadZipFile:
        # Handle the case where the file is not a valid ZIP file
        # os.remove(source)
        print("zipped file can't be unzipped. Either it is corrupt or not a correct zipped file", source)
        return False
    except Exception as e:
        # Handle any other exceptions
        print("exception occured", e, source)
        return False

    # walk into the each folder / subfolders inside given source and perform action on each file
    for root, dirs, files in os.walk(destination):
        for file_name in files:
            new_source = os.path.join(root, file_name)

            process_file(row, new_source)

            try:
                # once action done remove xml file 
                os.remove(new_source)
            except:
                pass
        return True

    return False


# main function to create article objects from archive articles
@api_view(['GET'])
def migrate_to_step2(request):
    # get the records from arhived article that are not processed
    # This includes new records as well as records that are modified
    qs = Archive.objects.all().exclude(status="processed")

    # looping through each object in the query set
    for row in qs:
        source = 'ARCHIVE/' + row.file_content.name
        destination = 'TEMP/' + source[:-4]
        # Create the output folder if it doesn't exist
        if not os.path.exists(destination):
            os.makedirs(destination)

        # if record is of type zip than sequence of action will be 
        # 1: unzip the content
        # 2: create / update records in article for each xml files
        # process_file is called inside unzip_file method itself
        if row.file_type in ('.zip', '.ZIP'):
            if unzip_file(source, destination, row):
                try:
                    shutil.rmtree(destination)
                except Exception as e:
                    pass
        
        else:
            process_file(row, source)
            
        update_archive(row)


    return Response("Successfully migrated all files")