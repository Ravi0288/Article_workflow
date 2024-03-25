import ftplib
from django.http import HttpResponse
import os
from rest_framework.decorators import api_view
from .archive_article import Archived_article_attribute
from .archive_article import Archived_article_attribute
from .providers import Provider_meta_data_FTP
import datetime
from io import BytesIO

import shutil
import os
from .common import is_ftp_content_folder
import pytz


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
            provider = item.provider,
            processed_on = datetime.datetime.now(tz=pytz.utc),
            status = 'success',
            file_size = file_size,
            file_type = file_type
        )
        x.file_content.save(article, content)
        return
    
    # if file exists than check the file size. If file size is different update the existing record
    if (x.exists() and not (x[0].file_size == file_size)):
        content = BytesIO()
        ftp_connection.retrbinary(f'RETR {article}', content.write)
        content.seek(0)
        x[0].status = 'success'
        x[0].file_content.save(article, content)
        return
    

# function to download folder with its content and convert to zip, finally save to table
def download_folder_from_ftp_and_save_zip(article, item):
    article = article + '.zip'
    zip_name = item.provider.official_name
    # Create a temporary directory to store downloaded files
    temp_dir = 'temp_download/' + item.provider.official_name
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    # Create a zip file from the downloaded content
    zip_filename = os.path.join(temp_dir, zip_name)
    zipped_file = shutil.make_archive(zip_filename.split('.')[0], 'zip', temp_dir)

    x = Archived_article_attribute.objects.filter(file_name_on_source=article)

    # if file not exists in database, create new record
    if not(x.exists()):
        # Save the zip file to the Django model
        with open(zipped_file, 'rb') as zip_file:
            zip_file.seek(0)
            # zip_file_model = ZipFileModel(name=zip_name)
            # zip_file_model.zip_file.save(zip_name + '.zip', ContentFile(zip_file.read()), save=True)

            x = Archived_article_attribute.objects.create(
                file_name_on_source = article,
                provider = item.provider,
                processed_on = datetime.datetime.now(tz=pytz.utc),
                status = 'success',
                file_size = os.path.getsize(zipped_file),
                file_type = '.zip'
            )

            x.file_content.save(article, zip_file)

        # Cleanup temporary directory and return
        shutil.rmtree(temp_dir)
        return

    # if file exists than check the file size. If file size is different update the existing record
    if (x.exists() and not (x[0].file_size == os.path.getsize(zipped_file))):
        x[0].status = 'success'
        with open(zipped_file, 'rb') as zip_file:
            zip_file.seek(0)
            x[0].file_content.save(article, zip_file)
            
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
            item.last_pull_time = datetime.datetime.now(tz=pytz.utc)
            item.last_pull_status = 'failed'
            item.last_error_message = e
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
                    if is_ftp_content_folder(ftp_connection, article):
                        # download the folder
                        download_folder_from_ftp_and_save_zip(article, item)
                    else:
                        # download the file
                        download_file(ftp_connection, article, item)
                except Exception as e:
                    pass

        # update the last status
        item.last_pull_time = datetime.datetime.now(tz=pytz.utc)
        item.last_pull_status = 'success'
        item.next_due_date = datetime.datetime.now(tz=pytz.utc) + datetime.timedelta(item.minimum_delivery_fq)
        item.save()

        # quite the ftp_connectionion
        ftp_connection.quit()

    return HttpResponse("done")



