from django.conf import settings
from step1.archive import Archive
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet
from model.article import Unreadable_xml_files, Article_attributes
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import xml.etree.ElementTree as ET
import pytz
import datetime
import shutil
import xmltodict
import os
import zipfile
from django.views.decorators.csrf import csrf_exempt

# Unreadable xml file serializer
class Unreadable_xml_files_serializers(ModelSerializer):
    class Meta:
        model = Unreadable_xml_files
        fields = '__all__'

# Unreadable xml file view sets
class Unreadable_xml_files_viewset(ModelViewSet):
    serializer_class = Unreadable_xml_files_serializers
    queryset = Unreadable_xml_files.objects.all()
    
    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.GET
        qs = qs.filter(**params.dict())
        return qs


# Article attribute serializer
class Article_attributes_serializer(ModelSerializer):
    class Meta:
        model = Article_attributes
        fields = '__all__'


# Article attribute viewset
class Article_attributes_viewset(ModelViewSet):
    queryset = Article_attributes.objects.all()
    serializer_class = Article_attributes_serializer

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.GET
        qs = qs.filter(**params.dict())
        return qs



# Function to read file line by line and compare their content
def compare_files_line_by_line(file1, file2):
    # read the files
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        # zip them together and read line by line
        for line1, line2 in zip(f1, f2):
            # compare read lines
            if line1 != line2:
                return False
    return True



# Read xml file and return dictionary
def read_xml_file(xml_file_path):
    try:
        # Open file
        with open(file=xml_file_path, mode='rb') as xml_txt:                 
            # Replace special character
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
        # If any invalid xml file found backup the file to INVALID_XML_FILES file for checking purposes
        destination = os.path.join(settings.BASE_DIR, 'INVALID_XML_FILES')
        dest = shutil.copy(xml_file_path, destination)
        Unreadable_xml_files.objects.create(
            file_name = dest,
            error_msg = e,
            source = xml_file_path.replace('TEMP/','').replace('\\', '/')
        )
        return None


# Function to check if the xml file has <article> or <ArticleSet> tag
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


# Update archive artile flags if processed
def update_archive(row):
    row.status = "processed"
    row.is_content_changed = 0
    row.processed_on = datetime.datetime.now(tz=pytz.utc)
    row.save()


# Create new objects in article table
def create_new_object(source, row, note):
    # Changing the default settings base directory root
    settings.MEDIA_ROOT = settings.BASE_DIR / 'ARTICLES'
    try:
        # Create new record
        qs = Article_attributes()
        qs.type_of_record = 'article'
        qs.provider = row.provider
        qs.archive = row
        qs.last_step = 1
        qs.last_status = 'active'
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
        # If exception occures create new record with status as failed
        Article_attributes.objects.create(
            title = "Error occured for Archive Article id number  " + str(row.id) + " and file path : " + row.file_content.name,
            type_of_record = 'N/A',
            provider = row.provider,
            archive = row,
            last_step = 1,
            last_status = 'failed',
            note = e,
            # DOI = row.unique_key,
            PID = "A locally assign identifier",
            MMSID = "The article's Alma identfier",
            provider_rec = "identifier"   
        )
        return False



# If archived articles are updated than we need to update articles file
# This function to be used for records with json/xml files
def update_exisiting_object_single_file(source, row):
    # Source may be ARCHIVE or TEMP based on from where this method is being called.
    # Making correct path from the received source
    destination = 'ARTICLES/' + (source.replace('ARCHIVE/','').replace('TEMP/',''))

    # If article record is changed, update its status to active
    q = Article_attributes.objects.get(archive__id=row.id)
    q.last_status = 'active'
    q.save()

    # Replace the destination file with the source file
    shutil.copyfile(source, destination)
    return True


# If archived articles are updated than we need to update articles file
# This function to be used for records with .zip files
def update_exisiting_object_zipped_file(source, row):
    # Source may be ARCHIVE or TEMP based on from where this method is being called.
    # Making correct path from the received source
    destination = (source.replace('ARCHIVE/','').replace('TEMP/','').replace('\\','/'))
    q = Article_attributes.objects.filter(archive__id=row.id)
    for item in q:
        print(item.article_file)
    q = q.filter(article_file=destination)
    destination = 'ARTICLES/' + destination
    # Get the article record by archive_id and file_name.
    # If record is present this file is available

    if q.exists():

        # compare content of source and destination files. If content are equal, no action required
        if compare_files_line_by_line(source, destination):
            return True

        # If article record found, update it's status to active
        q[0].last_status = 'active'
        q[0].save()
        # Replace the destination file with the source file
        shutil.copyfile(source, destination)
        return True
    else:
        # If recrod is not available with file_name it means this is a new file entered in the zipped file
        # Create new record
        create_new_object(source, row, 'success')



# In case the article objects are updated we need to fetch all the records that were packed in single xml file.
def prepocess_records_of_segregated_xml_files(xml_file_path, title, row):
    qs = Article_attributes.objects.filter(article_file__startswith = xml_file_path, title=title)
    if qs.exists():
        update_exisiting_object_single_file(xml_file_path, row)
    else:
        create_new_object(xml_file_path, row, 'success')


# Create xml file
def create_xml_file(file_name, file_content):
    try:
        root = ET.Element('root')  # Create a root element
        name_element = ET.SubElement(root, 'article')  # Create a sub-element <name>
        name_element.text = 'hello'  # Set the text content of <name>

        # Convert the XML structure to a string
        xml_str = ET.tostring(root, encoding='unicode', method='xml')

        # Write the XML string to a file
        with open(file_name, 'w') as file:
            file.write(file_content)
    except Exception as e:
        print("exception occured while writing the data 214", e)


# Segregate the file if multiple record found, and save the file with same name prefixing underscore_index
def segregate_article(article_set, xml_file_path, row):
    # Create the output folder if it doesn't exist
    if not os.path.exists(xml_file_path):
        os.makedirs(xml_file_path)

    for index, item in enumerate(article_set):
        try:
            file_name = str(xml_file_path[:-4]) + '_' + str(index+1) + '.xml'
            create_xml_file(file_name, item)
            prepocess_records_of_segregated_xml_files(xml_file_path, "None", row)
        except Exception as e:
            print(e, "article_set in", xml_file_path)

    try:
        # Delete the old file
        os.remove(xml_file_path)
    except:
        pass


# Function to check if the file has more than one record
def is_mulitple_record(xml_file_path, row):
    # with open(xml_file_path, 'r') as f:
    #     # Parse the XML data
    #     data = f.read()
    #     f.close()
    doc = read_xml_file(xml_file_path)

    ele = doc.get("ArticleSet", None)
    if ele:
        try:
            root = ET.fromstring(str(doc))
            # Find the 'ArticleSet' tag
            article_set = root.find('ArticleSet')

            if article_set is not None:
                segregate_article(article_set, xml_file_path, row)
                return True
            else:
                return False
        except Exception as e:
            print("Exception occured 251", e)



# Function to unzip
# This function will iterate through each directory / subdirectory of archive and will find the .zip / .ZIP file.
# If file found the function will unzip the content to the same path under articles directory
def unzip_file(source, destination, row):
    try:
        # unzip the source file to destination path
        with zipfile.ZipFile(source, 'r') as zip_ref:
            zip_ref.extractall(destination)
        zip_ref.close()

    except zipfile.BadZipFile:
        # Handle the case where the file is not a valid ZIP file
        # os.remove(source)
        print("Error occured while unizipping the zipped file can't be unzipped. Please check the file", source)
        return False
    except Exception as e:
        # Handle any other exceptions
        print("exception occured", e, source)
        return False

    # Walk into the each folder / subfolders inside given source and perform action on each file
    for root, dirnames, filenames in os.walk(destination):

        for file_name in filenames:
            new_source = os.path.join(root, file_name)
            if file_name.endswith('.xml'):
                # If xml file found jsonify it and perform update / create based on row.is_content_changed flag
                process_xml_file(new_source, row, 'zipped')
            elif file_name.endswith('.json'):

                # If json file found create record / update the record based on archive article flag
                process_json_file(new_source, row)

            else:
                # Almost every folder/subfolders have text file for info purpose to the list of files / filders inside the path
                # We dont need to keep this file hence deleting. In case any other purpose requires the same can be implement here
                print(file_name, "is other than xml/json/zip.")
                # Removing the file that is not xml or json
                try:
                    os.remove(new_source)
                except:
                    pass

    return True



# Processing xml file
# This function to be used with single xml file as well as unzipped xml_files. 
# Archive_destination variable is the indicator if xml is single source or unzipped.
# If this function is called for a xml file of unzipped directory than its value to archive_destination='zippped'
def process_xml_file(source, row, archive_destination):
    # Some file got the wrong xml format, 
    # Hence caused to stop the execution. Using try except to ignore the error due to corrupted xml files

    result = is_article_tag_available(source)

    if not result:
        # Remove the xml file if not a valid xml file. 
        os.remove(source)
        return False
    else:
        # Check if multiple records found
        # If multiple file found than it will be processed in is_mulitple_record function itself.
        if not is_mulitple_record(source, row):
            # If json file found create record / update the record based on archive article flag
            if row.is_content_changed:
                if archive_destination=='zipped':
                    update_exisiting_object_zipped_file(source, row)
                else:
                    update_exisiting_object_single_file(source, row)
            else:
                create_new_object(source, row, "success")

        # Remove the xml file
        os.remove(source)
        return True
        


# Processing xml file
def process_json_file(source, row):
    if row.is_content_changed:
        update_exisiting_object_single_file(source, row)
    else:
        create_new_object(source, row, "success")

    try:
        # Once action done remove xml file 
        os.remove(source)
    except:
        pass


# Main function to create article objects from archive articles
# @api_view(['GET'])
@login_required
@csrf_exempt
def migrate_to_step2(request):
    
    # Get the records from arhived article that are not processed
    # This includes new records as well as records that are modified
    qs = Archive.objects.all().exclude(status="processed")

    # if no file pending for migrations to step 2, return
    if qs.count() == 0:
        context = {
            'heading' : 'Message',
            'message' : 'No pending file available to be migrated to step 2'
        }
        return render(request, 'common/dashboard.html', context=context)

    # Looping through each object in the query set
    for row in qs:
        source = 'ARCHIVE/' + row.file_content.name
        destination = 'TEMP/' + source[:-4]
        # Create the output folder if it doesn't exist
        if not os.path.exists(destination):
            os.makedirs(destination)

        # If record is of type zip than sequence of action will be 
        # 1: Unzip the content
        # 2: Read each file, if json, copy it, if xml, process it 
        # 3: Create / update records in article for each json/xml files
        if row.file_type in ('.zip', '.ZIP'):
            if unzip_file(source, destination, row):
                update_archive(row)
                try:
                    shutil.rmtree(destination)
                except Exception as e:
                    pass

        # If file is json than create / update record in article 
        elif row.file_type == '.json':
            # Update or create record in article based on row.is_content_changed tag
            if row.is_content_changed:
                result = update_exisiting_object_single_file(source, row)
            else:
                result = create_new_object(source, row, "success")

            # Update the status of archived article record
            if result:
                update_archive(row)

        # If record is of type xml than sequence of action will be 
        # 1: Read each file, if ArticleSet found, segregate the files or just copy from xml
        # 2: Create / update records in article_attribute
        elif row.file_type == '.xml':
            if process_xml_file(source, row, 'independent_file'):
                update_archive(row)
        else:
            print("Unsupported file type found", source)

    context = {
        'heading' : 'Message',
        'message' : 'Successfully executed the step 2 migration process'
    }

    return render(request, 'common/dashboard.html', context=context)