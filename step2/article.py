from django.db import models
from django.conf import settings
from step1.archive_article import Archived_article
from step1.providers import Providers
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view
from rest_framework.response import Response
import zipfile
import xmltodict
import os
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.core.files.base import ContentFile
import json
import pytz
import datetime
import shutil
from .common.find_doi import find_doi
from .common.find_title import find_title
from xml.dom import minidom

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


# article attribute model
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


# article attribute serializer
class Article_attributes_serializer(ModelSerializer):
    class Meta:
        model = Article_attributes
        fields = '__all__'


# article attribute viewset
class Article_attributes_viewset(ModelViewSet):
    queryset = Article_attributes.objects.all()[:10]
    serializer_class = Article_attributes_serializer



# import xml.etree.ElementTree as ET
# import json

# def convert_xml_to_json(xml_string):
#     # Replace '&' with '&amp;' in the XML string
#     xml_string = xml_string.replace(b'&', b'&amp;')
    
#     # Parse the XML string
#     root = ET.fromstring(xml_string)
    
#     # Convert XML to JSON
#     xml_dict = {root.tag: xml_to_dict(root)}
#     xmltodict.parse(xml_txt, encoding='utf-8')
#     json_data = json.dumps(xml_dict)
    
#     return json_data

# def xml_to_dict(element):
#     # Convert XML element to dictionary
#     result = {}
#     for child in element:
#         if child:
#             if len(child) == 1 and child[0].tag == "text":
#                 # Handle text content
#                 result[child.tag] = child[0].text
#             else:
#                 # Recursively convert child elements
#                 result[child.tag] = xml_to_dict(child)
#         else:
#             result[child.tag] = child.text if child.text else ''
#     return result


# read json file and return dictionary
def read_json_file(xml_file_path):
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
        shutil.copy(xml_file_path, destination)
        return None


# function to check if the xml file has <article> or <ArticleSet> tag
# Any file that have no <article> / <ArticleSet> tag at root shall be discarded
# If condition meets this functio will return the file content as dictionary otherwise will return boolean False
'''
NAL receives data from different sources and the data structures of any xml files should  be in this formate
<article>, <Article>, <mods>, {}, [{}]. If any file not following this structres that file may be ommited
'''
def is_article_tag_available(xml_file_path):

    doc = read_json_file(xml_file_path)
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
def update_archive_article(row):
    row.is_processed = True
    row.processed_on = datetime.datetime.now(tz=pytz.utc)
    row.save()


# if archived articles are updated than we need to update articles file
def update_exisiting_object(source, row):
    # changing the default settings base directory root
    settings.MEDIA_ROOT = settings.BASE_DIR / 'ARTICLES'
    source = source.replace('ARCHIVE_ARTICLE/','').replace('TEMP/','')
    qs = Article_attributes.objects.filter(article_file = source)[0]
    with open(source, 'rb') as f:
        file_content = json.load(f)
        qs.title = find_title(file_content)
        f.seek(0)
        qs.article_file.save(source, ContentFile(f.read()))
        return True


# create new objects in article table
def create_new_object(source, row):
    # changing the default settings base directory root
    settings.MEDIA_ROOT = settings.BASE_DIR / 'ARTICLES'
    try:
        # create new record
        qs = Article_attributes()
        qs.type_of_record = 'article'
        qs.provider = row.provider
        qs.archive = row
        qs.last_stage = 2
        qs.last_status = 'completed'
        qs.note = "success"
        qs.PID = "A locally assign identifie"
        qs.MMSID = "The article's Alma identifer"
        qs.provider_rec = "indentf"

        x = source.replace('ARCHIVE_ARTICLE/','')
        x = x.replace('TEMP/','')
        with open(source, 'rb') as f:
            file_content = json.load(f)
            qs.title = find_title(file_content)
            qs.DOI = find_doi(file_content)
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
            last_stage = 2,
            last_status = 'failed',
            note = e,
            DOI = row.unique_key,
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
        create_new_object(json_file_path, row)


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
                title = find_title(item)
                prepocess_records_of_segregated_xml_files(json_file_path, title, row)
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
# This function will iterate through each directory / subdirectory of archive_article and will find the .zip / .ZIP file.
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
        print("zipped file cant be unzipped. it is corrupt or unsupported zipped file", source)
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
                        create_new_object(new_source, row)

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
                    os.remove(new_source)
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
        # remove the xml file
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
                    create_new_object(json_file_name, row)

            # remove the xml file
            os.remove(source)
            return True
        
        except Exception as e:
            print("exception occured while jsonifying the xml content", e, source)
            return False


# main function to create article objects from archive articles
@api_view(['GET'])
def migrate_to_step2(request):
    # get the records from arhived article that are not processed
    # This includes new records as well as records that are modified
    qs = Archived_article.objects.filter(is_processed=False)

    # looping through each object in the query set
    for row in qs:
        source = 'ARCHIVE_ARTICLE/' + row.file_content.name
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
                update_archive_article(row)
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
                result = create_new_object(source, row)

            # update archived article 
            if result:
                update_archive_article(row)
            # os.remove(destination[:-1] + '.json')

        # if record is of type xml than sequence of action will be 
        # 1: read each file and ensure all are jsonified from xml
        # 2: create / update records in article for each json files
        elif row.file_type == '.xml':
            if jsonify_file_content(source, row):
                update_archive_article(row)
        else:
            print("unsupported file type found", source)


    return Response("executed succcessfully")




#################################################################################################################
# functions for testing purpose only
@api_view(['GET'])
def update_doi(request):
    # qs = Article_attributes.objects.all()
    # i = 0
    # j = 0
    # x = []
    # for q in qs:
    #     i = i + 1
    #     path = 'ARTICLES/' + q.article_file.name
    #     if q.DOI is None:
    #         with open(path, 'rb') as e:
    #             f = json.load(e)
    #             x = find_doi(f)
    #             # q.DOI = x
    #             # q.save()
    #             if x == None:
    #                 i = i+1
    #             else:
    #                 j = j+1

    # return Response({"done": j, "not-done":i})

    q = Article_attributes.objects.get(pk=23770)
    path = 'ARTICLES/' + q.article_file.name
    print(path)
    with open(path, 'rb') as e:
        f = json.load(e)
        x = find_doi(f)
    return Response(x)

@api_view(['GET'])
def update_title(request):
    qs = Article_attributes.objects.all()
    i = 0
    j = 0
    for q in qs:
        if q.title in (None, ''):
            path = 'ARTICLES/' + q.article_file.name
            with open(path, 'rb') as e:
                f = json.load(e)
                x = find_title(f)
                if x == None:
                    j=j+1
                    print("######################", path, "not update")
                else:
                    i = i + 1

            try:
                q.save()
            except Exception as e:
                print("#########################333", path ,"#########################333")
    return Response(str(j))
        

@api_view(['GET'])
def check_title(request):
    # find title of the json content
    with open('ARTICLES/Hindawi/hindawi_2019_12_2/volume-2019/journals/JAMC/8970624.ref.json','rb') as f:
        json_obj =  json.load(f)

    x = find_title(json_obj)
    return Response(x)

@api_view(['GET'])
def check_doi(request):
    # find title of the json content
    with open('ARTICLES/Hindawi/hindawi_2018_10_1/volume-2018/journals/IJG/7329576.json','rb') as f:
        json_obj =  json.load(f)

    x = find_doi(json_obj)
    return Response(x)


@api_view(['GET'])
def find_key_main(request):
    target_key='doi'
    f2='DOI'
    settings.MEDIA_ROOT = settings.BASE_DIR / 'ARTICLES'

    qs = Article_attributes.objects.all()[:5]
    
    i = 0
    j = 0
    count = qs.count()
    l = 0
    arr = []    
    for x in qs:
        with open(x.article_file.path, 'r') as f:
            data = json.load(f)

    def extract(obj, arr, key, i):
        x = str(obj)
        print(('doi' in x), "smallllllll")
        print(('DOI' in x), "uppper")
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key, i)
                elif k.upper() == key:
                    i = i + 1
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key, i)

        return {'arr':arr, 'i':i}

    results = extract(data, arr, 'DOI', i)

        
    return Response({"msg" :arr, 'i':i, 'c':count})



@api_view(['GET'])
def test_xml(request):
    # for root, dit, files in os.walk('ARTICLE'):
    path = 'E:\\NAL-USDA\\NAL_LIBRARY_SYSTEM\\INVALID_XML_FILES\\AN18724_COabs.xml'
    is_article_tag_available(path)
    return Response("done")