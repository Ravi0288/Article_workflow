from django.conf import settings
from step1.archive import Archive
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view
from rest_framework.response import Response
from model.article import Unreadable_xml_files, Article_attributes
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

import json
import pytz
import datetime
import shutil
import xmltodict
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



# read xml file and return dictionary
def read_xml_file(xml_file_path):
    try:
        # open file
        with open(file=xml_file_path, mode='rb') as xml_txt:                 
            # replace special character
            xml_txt = xml_txt.read().replace(
                b'&', b'&amp;').replace(
                    b'""epub""', b'"epub"').replace(
                        b'<i>',b'').replace(
                            b'</i>', b''
                        ).replace(
                            b' < ', b' less than '
                        ).replace(
                            b' > ', b' greater than '
                        )

            return xmltodict.parse(xml_txt, encoding='utf-8')
    except Exception as e:
        # if any invalid xml file found backup the file to INVALID_XML_FILES file for checking purposes
        destination = os.path.join(settings.BASE_DIR, 'INVALID_XML_FILES')
        dest = shutil.copy(xml_file_path, destination)
        Unreadable_xml_files.objects.create(
            file_name = dest,
            error_msg = e
        )
        return None


# function to check if the xml file has <article> or <ArticleSet> tag
# Any file that have no <article> / <ArticleSet> tag at root shall be discarded
# If condition meets this functio will return the file content as dictionary otherwise will return boolean False
'''
NAL receives data from different sources and the data structures of any xml files should  be in this formate
<article>, <Article>, <mods>, {}, [{}]. If any file not following this structres that file may be ommited
'''
def is_article_tag_available(xml_file_path):

    doc = read_xml_file(xml_file_path)
    if not doc:
        return False
    
    ele = doc.get("article", None)
    if ele:
        # print("article tag found. File will be saved for stage 2")
        return doc
    
    ele = doc.get("Article", None)
    if ele:
        # print("article tag found. File will be saved for stage 2")
        return doc
    
    ele = doc.get("mods", None)
    if ele:
        # print("article tag found. File will be saved for stage 2")
        return doc

    ele = doc.get("ArticleSet", None)
    if ele:
        # print("article set found. File will be saved for stage 2")
        # print(xml_file_path)
        return doc

    # print("article / ArticleSet tag not found. File skipped")
    return False



# update archive artile flags if processed
def update_archive(row):
    row.status = "processed"
    row.processed_on = datetime.datetime.now(tz=pytz.utc)
    row.save()


# if archived articles are updated than we need to update articles file
def update_exisiting_object(source, row):
    # changing the default settings base directory root
    settings.MEDIA_ROOT = settings.BASE_DIR / 'ARTICLES'
    source = source.replace('ARCHIVE/','').replace('TEMP/','')
    qs = Article_attributes.objects.filter(article_file = source)[0]
    with open(source, 'rb') as f:
        file_content = json.load(f)
        # qs.title = find_title(file_content)
        f.seek(0)
        qs.article_file.save(source, ContentFile(f.read()))
        return True


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
            # file_content = json.load(f)
            # qs.title = find_title(file_content)
            # qs.DOI = find_doi(file_content)
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
            # DOI = row.unique_key,
            PID = "A locally assign identifie",
            MMSID = "The article's Alma identifer",
            provider_rec = "identifier"   
        )
        return False


# in case the article objects are updated we need to fetch all the records that were packed in single xml file.
def prepocess_records_of_segregated_xml_files(json_file_path, title, row):
    qs = Article_attributes.objects.filter(article_file__startswith = json_file_path[:5], title=title)
    if qs.exists():
        update_exisiting_object(json_file_path, row)
    else:
        create_new_object(json_file_path, row, "success")


# segregate the file if multiple record found, and save the file with same name prefixing underscore_index
def segregate_article(article_set, json_file_path, row):
    # Create the output folder if it doesn't exist
    if not os.path.exists(json_file_path):
        os.makedirs(json_file_path)
    if article_set:
        for index, item  in enumerate(article_set):
            try:
                file_name = str(json_file_path[:-5]) + '_' + str(index+1) + '.json'
                with open(file_name, 'w') as f:
                    json.dump(item,f)
                    f.close()
                # title disabled in stage 2
                # title = find_title(item)
                prepocess_records_of_segregated_xml_files(json_file_path, "None", row)
            except Exception as e:
                print(e, "article_set in", json_file_path)

    try:
        # delete the old file
        os.remove(json_file_path)
    except:
        pass


# function to check if the file has more than one record
def is_mulitple_record(json_file_path, row):
    with open(json_file_path, 'r') as file:
        data = json.load(file)
        obj = data.get('ArticleSet', None)
        if obj and (len(obj) > 1):
            segregate_article(obj.get('Article', None), json_file_path, row)
            return True
        else:
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
            if not file_name.endswith('.xml'):
                # some folders have got files other than xml format.
                if file_name.endswith('.json'):
                    # if json file found create record / update the record based on archive article flag
                    if row.is_content_changed:
                        update_exisiting_object(new_source, row)
                    else:
                        create_new_object(new_source, row, "success")

                    try:
                        # once action done remove xml file 
                        os.remove(new_source)
                    except:
                        pass

                elif not file_name.endswith('.json'):
                    # almost every folder/subfolders have text file for info purpose to the list of files / filders inside the path
                    # We dont need to keep this file hence deleting. In case any other purpose requires the same can be implement here
                    print(file_name, "is not of xml type. If known file, new action may be implemented here")
                    # removing the file that is not xml or json
                    try:
                        os.remove(new_source)
                    except:
                        pass
            else:
                # if xml file found jsonify it and perform update / create based on row.is_content_changed flag
                jsonify_file_content(new_source, row)
        return True

    return False


# if the content is of type xml, this function will jsonify the content, will save the json file to temporary location and 
# finally new record will be created or the existing file will be updated based in row.is_content_changed flag
def jsonify_file_content(source, row):
    # some file got the wrong xml format, 
    # hence caused to stop the execution. Using try except to ignore the error due to corrupted xml files

    json_data = is_article_tag_available(source)

    if not json_data:
        # remove the xml file if not a valid xml file. 
        os.remove(source)
        return False
    else:
        try:
            # read the xml file and save as json to the same path
            json_file_name = source[:-4] + '.json'
            with open(json_file_name, "w") as f:
                json.dump(json_data, f)
            f.close()

            # check if multiple records found inside the same file
            # if multiple file found than it will be processed in is_mulitple_record function itself.
            if not is_mulitple_record(json_file_name, row):
                # if json file found create record / update the record based on archive article flag
                if row.is_content_changed:
                    update_exisiting_object(json_file_name, row)
                else:
                    create_new_object(json_file_name, row, "success")

            # remove the xml file
            os.remove(source)
            return True
        
        except Exception as e:
            print("exception occured while jsonifying the xml content", e, source)
            create_new_object(json_file_name, row, e)
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
        # 2: read each file and ensure all are jsonified from xml
        # 3: create / update records in article for each json files
        if row.file_type in ('.zip', '.ZIP'):
            if unzip_file(source, destination, row):
                update_archive(row)
                try:
                    shutil.rmtree(destination)
                except Exception as e:
                    pass

        # if file is json than create / update record in article 
        elif row.file_type == '.json':
            # update or create record in article based on row.is_content_changed tag
            if row.is_content_changed:
                result = update_exisiting_object(source, row)
            else:
                result = create_new_object(source, row, "success")

            # update archived article 
            if result:
                update_archive(row)
            # os.remove(destination[:-1] + '.json')

        # if record is of type xml than sequence of action will be 
        # 1: read each file and ensure all are jsonified from xml
        # 2: create / update records in article for each json files
        elif row.file_type == '.xml':
            if jsonify_file_content(source, row):
                update_archive(row)
        else:
            print("unsupported file type found", source)


    context = {
        'heading' : 'Message',
        'message' : 'Successfully migrated all files to steo 2'
    }

    return render(request, 'accounts/dashboard.html', context=context)
    # return Response("Successfully migrated all files")