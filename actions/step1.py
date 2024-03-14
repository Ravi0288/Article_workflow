import ftplib
from django.http import HttpResponse
import os
from rest_framework.decorators import api_view
from .archive_article import Archived_article_attribute
from .archive_article import Archived_article_attribute
from .providers import Provider_meta_data_FTP, Provider_meta_data_API
import datetime
from io import BytesIO
import requests
from django.core.files.base import ContentFile
import zipfile
from rest_framework.response import Response
import shutil
import os
from .common import is_ftp_content_folder


# function to unzip the file
def unzip_files():
    qs = Archived_article_attribute.objects.filter(status="waiting", file_type__in = ('.tar','.zip'))
    print(qs.count())
    for item in qs:
        try:
            with zipfile.ZipFile(item.file_content, 'r') as zip_ref:
                # Extract the contents of the zip file
                filepath =(item.file_content.name).split('.')
                zip_ref.extractall(filepath[0])
        except Exception as e:
            pass
    return Response("done")


# function to download file
def download_file(ftp_connection, article, item):
    file_size = ftp_connection.size(article)
    # if record not downloaded in our record and the the file size is not zero than download and write to our database
    x = Archived_article_attribute.objects.filter(file_name_on_source=article)

    # if file not exists in database, create new record
    if not(x.exists()):
        content = BytesIO()
        ftp_connection.retrbinary(f'RETR {article}', content.write)
        content.seek(0)
        file_type = os.path.splitext(article)[1]
        x = Archived_article_attribute.objects.create(
            file_name_on_source = article,
            provider = item.provider.official_name,
            processed_on = datetime.datetime.today(),
            status = 'waiting',
            file_size = file_size,
            file_type = file_type
        )
        x.file_content.save(article, content)
        return

    # if file exists than check the file size. If file size is different update the existing record
    if (x.exists() and not (x.file_size == file_size)):
        x.status = 'waiting'
        x.file_content.save(article, content)
        return
        

# function to iterate folder. If another folder found in side the folder this function will call itself.
def download_folder(ftp_connection, article, item):
    ftp_connection.cwd(article)
    filenames = ftp_connection.nlst()
    for filename in filenames:
        if '.' in filename:  # It's a file
            download_file(ftp_connection, filename, item)
        else:  # It's a subfolder
            download_folder(ftp_connection, article, os.path.join(article, article))
    ftp_connection.cwd('..')
    return



# Function to download folder and convert to zip.
def download_and_save_zip_using_api(folder_url, article, item):
    # Example usage
    zip_name = article.provider.working_name

    # Create a temporary directory to store downloaded files
    temp_dir = 'temp_download'
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    # Download folder content
    response = requests.get(folder_url)
    if response.status_code == 200:
        content = response.text.split('\n')
        for item in content:
            if item.strip() != '':
                item_url = folder_url + '/' + item.strip()
                # Download file
                filename = os.path.join(temp_dir, item.strip())
                with open(filename, 'wb') as f:
                    f.write(requests.get(item_url).content)

        # Create a zip file from the downloaded content
        zip_filename = os.path.join(temp_dir, zip_name + '.zip')
        shutil.make_archive(zip_filename.split('.')[0], 'zip', temp_dir)

        x = Archived_article_attribute.objects.filter(file_name_on_source=article)

        # if file not exists in database, create new record
        if not(x.exists()):
            # Save the zip file to the Django model
            with open(zip_filename, 'rb') as zip_file:
                # zip_file_model = ZipFileModel(name=zip_name)
                # zip_file_model.zip_file.save(zip_name + '.zip', ContentFile(zip_file.read()), save=True)

                x = Archived_article_attribute.objects.create(
                    file_name_on_source = article,
                    provider = item.provider.official_name,
                    processed_on = datetime.datetime.today(),
                    status = 'waiting',
                    file_size = os.path.getsize(zip_filename),
                    file_type = '.zip'
                )
                x.file_content.save(article, zip_file)
                return

        # if file exists than check the file size. If file size is different update the existing record
        if (x.exists() and not (x.file_size == os.path.getsize(zip_filename))):
            x.status = 'waiting'
            x.file_content.save(article, zip_filename)
            return

        # Cleanup temporary directory
        shutil.rmtree(temp_dir)
    
    return


# function to download folder with its content and convert to zip, finally save to table
def download_folder_from_ftp_and_save_zip(ftp_connection, article, item):
    zip_name = article.provider.working_name
    # Create a temporary directory to store downloaded files
    temp_dir = 'temp_download'
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    # Download folder content
    filenames = ftp_connection.nlst()
    for filename in filenames:
        with open(os.path.join(temp_dir, filename), 'wb') as f:
            ftp_connection.retrbinary('RETR ' + filename, f.write)

    # Create a zip file from the downloaded content
    zip_filename = os.path.join(temp_dir, zip_name + '.zip')
    shutil.make_archive(zip_filename.split('.')[0], 'zip', temp_dir)

    x = Archived_article_attribute.objects.filter(file_name_on_source=article)

    # if file not exists in database, create new record
    if not(x.exists()):
        # Save the zip file to the Django model
        with open(zip_filename, 'rb') as zip_file:
            # zip_file_model = ZipFileModel(name=zip_name)
            # zip_file_model.zip_file.save(zip_name + '.zip', ContentFile(zip_file.read()), save=True)

            x = Archived_article_attribute.objects.create(
                file_name_on_source = article,
                provider = item.provider.official_name,
                processed_on = datetime.datetime.today(),
                status = 'waiting',
                file_size = os.path.getsize(zip_filename),
                file_type = '.zip'
            )
            x.file_content.save(article, zip_file)
            return

    # if file exists than check the file size. If file size is different update the existing record
    if (x.exists() and not (x.file_size == os.path.getsize(zip_filename))):
        x.status = 'waiting'
        x.file_content.save(article, zip_filename)
        return

    # Cleanup temporary directory
    shutil.rmtree(temp_dir)
    return



# this function will fetch article from the FTP
@api_view(['GET'])
def download_from_ftp(request):
    # get all providers that are due to be accessed today
    due_for_download = Provider_meta_data_FTP.objects.all()
    
    # if none is due to be accessed abort the process
    if not due_for_download.count():
        return HttpResponse("No pending action found")

    # if providers are due to be accessed
    for item in due_for_download:

        # try to ftp_connection to FTP, if error occures update the record
        try:
            ftp_connection = ftplib.FTP(item.server)
            ftp_connection.login(item.account, item.pswd)
        except Exception as e:
            item.last_pull_time = datetime.datetime.today()
            item.last_pull_status = 'failed'
            item.save()
            continue

        # read the destination location
        ftp_connection.cwd(item.site_path)
        article_library = ftp_connection.nlst()

        # if record found explore inside.
        if article_library:
            # iterate through each file
            for article in article_library:
                try:
                    # check if the article is file or directory
                    # if not (os.path.isdir(article)):
                    # if '.' in article:
                    if is_ftp_content_folder(ftp_connection, article):
                        # download the file
                        download_file(ftp_connection, article, item)
                    else:
                        # # iterate through the folder and download the files inside it 
                        # download_folder(ftp_connection, article, item)
                        # or
                        # download the folder, convert it to zip and store in database
                        download_folder_from_ftp_and_save_zip(ftp_connection, article, item)
                except Exception as e:
                    pass

        # update the last status
        item.last_pull_time = datetime.datetime.today()
        item.last_pull_status = 'waiting'
        item.next_due_date = datetime.datetime.today() + datetime.timedelta(item.minimum_delivery_fq)
        item.save()

        # quite the ftp_connectionion
        ftp_connection.quit()

    return HttpResponse("done")



@api_view(['GET'])
def download_from_api(request):
    # get all providers that are due to be accessed today
    due_for_download = Provider_meta_data_API.objects.all()
    
    # if none is due to be accessed abort the process
    if not due_for_download.count():
        return HttpResponse("No pending action found")

    # if providers are due to be accessed
    for item in due_for_download:
        # Send a GET request to the URL
        response = requests.get(item.base_url)
        if response.status_code == 200:
            # Retrieve file name and file size from response headers
            content_disposition = response.headers.get('content-disposition')
            if content_disposition:
                file_name = content_disposition.split('filename=')[1]
            else:
                file_name = (response.url).split('/')[-1] # Use URL as filename if content-disposition is not provided
            
            file_size = int(response.headers.get('content-length', 0))
            file_type = os.path.splitext(file_name)[1]

            # Open a local file with write-binary mode and write the content of the response to it
            qs = Archived_article_attribute.objects.filter(file_name_on_source=file_name) 

            # if file not available, create new record
            if not(qs.exists()):
                x = Archived_article_attribute.objects.create(
                    file_name_on_source = file_name,
                    provider = item.provider.official_name,
                    processed_on = datetime.datetime.today(),
                    status = 'waiting',
                    file_size = file_size,
                    file_type = file_type
                )

                # save file
                x.file_content.save(file_name, ContentFile(response.content))

            # if file already available, and size mismatch,update the record with updated file
            if (qs.exists() and not(qs.file_size == file_size)):
                qs[0].file_content.save(file_name, ContentFile(response.content))

            # update status
            item.last_pull_time = datetime.datetime.today()
            item.last_pull_status = 'waiting'
            item.next_due_date = datetime.datetime.today() + datetime.timedelta(item.minimum_delivery_fq)
            item.save()
        else:
            item.last_pull_time = datetime.datetime.today()
            item.last_pull_status = 'failed'
            item.save()
    return HttpResponse("done")






