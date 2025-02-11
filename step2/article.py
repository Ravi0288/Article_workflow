from step1.archive import Archive
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet
from model.article import Unreadable_files, Article
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import pytz
import datetime
import shutil
import os
import zipfile
from django.views.decorators.csrf import csrf_exempt
from splitter import splitter
from django.core.files import File
from django.core.files.storage import default_storage


# Unreadable xml file serializer
class Unreadable_files_serializers(ModelSerializer):
    class Meta:
        model = Unreadable_files
        fields = '__all__'

# Unreadable files view sets
class Unreadable_files_viewset(ModelViewSet):
    serializer_class = Unreadable_files_serializers
    queryset = Unreadable_files.objects.all()
    
    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.GET
        qs = qs.filter(**params.dict())
        return qs


# Article attribute serializer
class Article_serializer(ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'


# Article attribute viewset
class Article_viewset(ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = Article_serializer

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.GET
        qs = qs.filter(**params.dict())
        return qs


# Function to read file line by line and compare their content
# This function takes content of the file as string as input
def compare_files_line_by_line(f1, f2):
    for line1, line2 in zip(f1, f2):
        # compare read lines
        if line1 != line2:
            return False
    return True


# read file
def read_file(file_path):
    if isinstance(file_path, str):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        with open(file_path.name, 'r', encoding='utf-8') as f:
            return f.read()        


# Make entry of invalid xml
def create_invalid_xml_json(invalid_file_path, error_msg, file_name, file_type):
    destination = '/ai/metadata/INVALID_FILES/'

    # check if the same file entry is already exists.
    if Unreadable_files.objects.filter(file_content=file_name).exists():
        return True
    
    # if destination directory not available create
    if not os.path.exists(destination):
        os.makedirs(destination)

    # Read the file and make entry in invalid_files table
    file_name = '/ai/metadata/INVALID_FILES/' + file_name
    source = invalid_file_path.replace('\\', '/').replace('/ai/metadata/TEMP_DOWNLOAD','')
    with open(invalid_file_path, 'rb') as f:
        file_content = File(f)
 
        # dest = shutil.copy(invalid_file_path, file_name)
        x = Unreadable_files.objects.create(
            file_type = file_type.lower(),
            error_msg = error_msg,
            source = source
        )

        # Assign the File object to the file_content field and save the model instance
        x.file_content.save(os.path.basename(file_name), file_content)
        file_content.close()
    return True


# Update archive record
def update_archive(row):
    row.status = "processed"
    row.is_content_changed = False
    row.processed_on = datetime.datetime.now(tz=pytz.utc)
    row.save()


# Create new Article
def create_new_object(source, row, note, content):
    # Create new record
    qs = Article()
    qs.type_of_record = 'article'
    qs.provider = row.provider
    qs.archive = row
    qs.last_step = 2
    qs.last_status = 'active'
    qs.note = note

    # since the file is stored in temp file that contains TEMP_DOWNLOAD and ARCHIVE in its path. 
    # Just remove these strings and it becomes the correct media path where the file will stored
    x = (source.replace('\\','/')).split('/')[-1]

    try:
        if isinstance(content, str) and content.startswith("'"):
            content = content[1:].encode('utf-8')

        if isinstance(content, (list, tuple)):
            if isinstance(content[0], str):
                if content[0].startswith("'"): 
                    content[0] = (content[0][1:]).encode('utf-8')
                else:
                    content = (content[0]).encode('utf-8')

            if isinstance(content[0], (list, tuple)):
                if isinstance(content[0][0], str):
                    if content[0][0].startswith("'"):
                        content = (content[0][0][1:]).encode('utf-8')
                    else:
                        content = (content[0][0]).encode('utf-8')

        qs.article_file.save(x, ContentFile(content))

    except Exception as e:
        print("Couldn't create file : ", e)

    return True

# Update Archive
def update_article(article, note='', content=''):
    article.last_status = 'active'
    article.last_step = 2
    if note:
        article.note = note
    if content:
        file_name = article.article_file.name
        # delete the old file first
        # os.remove(article.article_file.path)
        old_file_path = article.article_file.path
        if os.path.exists(old_file_path):
            default_storage.delete(old_file_path)

        article.article_file.save(file_name, ContentFile(content))
    else:
        article.save()
    return True

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
        print("Error occurred while unizipping the file. Zipped file may be corrupt / invalid. Source : ", source)
        return False
    except Exception as e:
        # Handle any other exceptions
        print("exception occurred : ", e, ". Source : ", source)
        return False

    return True


# This function will run based on the result returned by the Splitter function.
# The function takes parameters as data (result of Splitter function, source=location of file, destingation= new location of file, archive_row=Arhive record row)
def process_success_result_from_splitter_function(data, source, destination, archive_row):

    # if single record found
    if len(data[0]) == 1:
        try:
            article = Article.objects.get(article_file=source)
            # compare content of the file line by line. If change found update the file else do nothinf
            with open(article.article_file.path, 'r', encoding='utf-8') as f1:
                if compare_files_line_by_line(f1,data[0]):
                    shutil.copy(source, destination.replace('TEMP_DOWNLOAD', ''))
                    update_article(article=article)
        except Article.DoesNotExist:
            create_new_object(source, archive_row, note="", content=data[0])


    # if multiple record found
    else:
        for index, line in enumerate(data[0]):
            if source.endswith("xml"):
                indexed_file_name = str(source[:-4]) + '_' + str(index) + '.xml'
            elif source.endswith('json'):
                indexed_file_name = str(source[:-5]) + '_' + str(index) + '.json'
            else:
                continue
            try:
                article = Article.objects.get(article_file=source)
                # compare content of the file line by line. If change found update the file else do nothing
                with open(article.article_file.path, 'r', encoding='utf-8') as f1:
                    if compare_files_line_by_line(f1,line):
                        update_article(article=article, content=line)
            except Article.DoesNotExist:
                create_new_object(indexed_file_name, archive_row, note="", content=line)


# Main function to create article objects from archive articles
# @api_view(['GET'])
@login_required
@csrf_exempt
def migrate_to_step2(request):
    
    # Get the records from arhived article that are not processed
    # This includes new records as well as records that are modified
    archive_records = Archive.objects.all().exclude(status="processed")

    # if no file pending for migrations to step 2, return
    if archive_records.count() == 0:
        context = {
            'heading' : 'Message',
            'message' : 'No pending file available to be migrated to step 2'
        }
        return render(request, 'common/dashboard.html', context=context)

    # Looping through each object in the query set
    for archive_row in archive_records:
        source = archive_row.file_content.path
        # If record is of type zip than sequence of action will be 
        # 1: Unzip the content
        # 2: Read each file, if json, copy it, if xml, process it 
        # 3: Create / update records in article for each json/xml files
        if archive_row.file_type in ('.zip', '.ZIP'):
            # Create the output folder if it doesn't exist. Output folder is source path prefixed by 'TEMP_DOWNLOAD' and .zip removed
            destination = '/ai/metadata/TEMP_DOWNLOAD' + source[:-4].replace('E:','').replace('\\', '/').replace('C:','').replace('D:','')
            if not os.path.exists(destination):
                os.makedirs(destination)
            
            # upzip the folder. unzip_file function returns True/False based on unzip status
            if unzip_file(source, destination, archive_row):
                # Check if the file is existing and the content the file file is changed than we need to perform update/create operation
                if archive_row.is_content_changed:
                    # Travers the each directory/subdirectories
                    for root, dir, filenames in os.walk(destination):
                        for file_name in filenames:
                            new_source = os.path.join(root, file_name)
                            data = splitter(read_file(new_source))

                            if data[1] == 'successful':
                                process_success_result_from_splitter_function(data, new_source, destination, archive_row)
                            else:
                                create_invalid_xml_json(new_source, "Invalid", file_name, file_name.split('.')[-1])
                
                # create all the row
                else:
                    for root, dir, filenames in os.walk(destination):
                        for file_name in filenames:
                            new_source = os.path.join(root, file_name)
                            data = splitter(read_file(new_source))

                            if data[1] == 'successful':
                                process_success_result_from_splitter_function(data, new_source, destination, archive_row)
                            else:
                                print("Splitter function returned error : ", data[1])
                                create_invalid_xml_json(new_source, "Invalid", file_name, file_name.split('.')[-1])


                # remove the unzipped directory from TEMP_DOWNLOAD location
                try:
                    shutil.rmtree(destination)
                except:
                    pass

        # If file is json/xml than create / update record in article 
        elif archive_row.file_type in ['.xml', '.json', '.JSON','.XML']:
            # Update or create record in article based on row.is_content_changed tag
            source = archive_row.file_content.path
            file_name = archive_row.file_content.name

            # with open(source, 'r', encoding='utf-8') as f:
            data = splitter(read_file(source))

            if data[1] == 'successful':
                destination = source.replace('ARCHIVE','ARTICLES')
                process_success_result_from_splitter_function(data, source, destination, archive_row)
            
            else:
                create_invalid_xml_json(source, "Invalid", file_name, file_name.split('.')[-1])

        # if file is other than xml/json/zip, ignore the file
        else:
            print("Unsupported file type found. Source : ", source)

        # update the row status
        update_archive(archive_row)

    # for loop ends here.
    # return the result to UI
    context = {
        'heading' : 'Message',
        'message' : 'All valid archive files have been successfully migrated to Step 2 and stored in the Article directory.'
    }

    return render(request, 'common/dashboard.html', context=context)