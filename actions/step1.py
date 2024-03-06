from .common import action, delete_file
import time
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


# function to download file
def download_file(connect, article, item):
    file_size = connect.size(article)
    # if record not downloaded in our record and the the file size is not zero than download and write to our database
    if not (Archived_article_attribute.objects.filter(file_name_on_ftp=article).exists()):
        content = BytesIO()
        connect.retrbinary(f'RETR {article}', content.write)
        content.seek(0)
        file_type = os.path.splitext(article)[1]
        x = Archived_article_attribute.objects.create(
            file_name_on_ftp = article,
            provider = item.provider.official_name,
            processed_on = datetime.datetime.today(),
            status = 'waiting',
            file_size = file_size,
            file_type = file_type
        )
        x.file_content.save(article, content)
        return


# function to iterate folder. If another folder found in side the folder this function will call itself.
def download_folder(connect, article, item):
    connect.cwd(article)
    filenames = connect.nlst()
    for filename in filenames:
        if '.' in filename:  # It's a file
            download_file(connect, filename, item)
        else:  # It's a subfolder
            download_folder(connect, article, os.path.join(article, article))
    connect.cwd('..')
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

        # try to connect to FTP, if error occures update the record
        try:
            connect = ftplib.FTP(item.server)
            connect.login(item.account, item.pswd)
        except Exception as e:
            item.last_pull_time = datetime.datetime.today()
            item.last_pull_status = 'failed'
            item.save()
            continue

        # read the destination location
        connect.cwd(item.site_path)
        article_library = connect.nlst()

        # if record found explore inside.
        if article_library:
            # iterate through each file
            for article in article_library:
                try:
                    # check if the article is file or directory
                    # if not (os.path.isdir(article)):
                    if '.' in article:
                        # download the file
                        download_file(connect, article, item)
                    else:
                        # iterate through the folder and download the files inside it 
                        download_folder(connect, article, item)
                except Exception as e:
                    pass

        # update the last status
        item.last_pull_time = datetime.datetime.today()
        item.last_pull_status = 'waiting'
        item.next_due_date = datetime.datetime.today() + datetime.timedelta(item.provider.minimum_delivery_fq)
        item.save()

        # quite the connection
        connect.quit()

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
                file_name = "xx"  # Use URL as filename if content-disposition is not provided
            file_size = int(response.headers.get('content-length', 0))
            file_type = os.path.splitext(file_name)[1]

            # Open a local file with write-binary mode and write the content of the response to it
            x = Archived_article_attribute.objects.create(
                file_name_on_ftp = file_name,
                provider = item.provider.official_name,
                processed_on = datetime.datetime.today(),
                status = 'waiting',
                file_size = file_size,
                file_type = file_type
            )

            # save file
            x.file_content.save('filename', ContentFile(response.content))

            # update status
            item.last_pull_time = datetime.datetime.today()
            item.last_pull_status = 'waiting'
            item.next_due_date = datetime.datetime.today() + datetime.timedelta(item.provider.minimum_delivery_fq)
            item.save()
        else:
            item.last_pull_time = datetime.datetime.today()
            item.last_pull_status = 'failed'
            item.save()

    return HttpResponse("done")

