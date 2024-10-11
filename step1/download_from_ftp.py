import ftplib

import os
from django.shortcuts import render
from .archive import Archive
from .provider import Provider_meta_data_FTP
import datetime
from io import BytesIO

import shutil
import os
from configurations.common import is_ftp_content_folder
import pytz
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
import socket

# This function will download each file/dir from SFTP server to the local directory
# in case of given folder is blank or have any kind of error this will return False
def download_directory_from_ftp(ftp_connection, remote_directory, local_directory):
    if not os.path.exists(local_directory):
        os.makedirs(local_directory)

    content_list = ftp_connection.nlst(remote_directory)

    if len(content_list) == 0:
        return False
    
    try:
        for entry in content_list:
            remote_path = os.path.join(remote_directory, entry)
            local_path = os.path.join(local_directory, entry)
            
            if is_ftp_content_folder(ftp_connection, remote_path):
                download_directory_from_ftp(ftp_connection, remote_path, local_path)
            else:
                with open(local_path, 'wb') as local_file:
                    ftp_connection.retrbinary(f'RETR {entry}', local_file.write)

        return True
    except Exception as e:
        print(e)
        return False

# function to download file
def download_file(ftp_connection, article, item):
    file_size = ftp_connection.size(article)
    # if record downloaded in our record and the the file size is not zero than download and write to our database
    x = Archive.objects.filter(file_name_on_source=article)

    # if file not exists in database, create new record
    if not(x.exists()):
        content = BytesIO()
        ftp_connection.retrbinary(f'RETR {article}', content.write)
        content.seek(0)
        file_type = os.path.splitext(article)[1]
        x = Archive.objects.create(
            file_name_on_source = article,
            provider = item.provider,
            processed_on = datetime.datetime.now(tz=pytz.utc),
            status = 'waiting',
            file_size = file_size,
            file_type = file_type
        )
        article = str(x.id) + '.' + article.split('.')[-1]
        x.file_content.save(article, content)
        return
    
    # if file exists than check the file size. If file size is different update the existing record
    if (x.exists() and not (x[0].file_size == file_size)):
        content = BytesIO()
        ftp_connection.retrbinary(f'RETR {article}', content.write)
        content.seek(0)
        x[0].status = 'active'
        x[0].is_content_changed = True
        article = str(x[0].id) + '.' + article.split('.')[-1]
        x[0].file_content.save(article, content)
        return
    

# function to download folder with its content and convert to zip, finally save to table
def download_folder_from_ftp_and_save_zip(ftp_connection, article, item):
    print("zipping content")
    temp_dir = '/ai/metadata/' + item.provider.official_name
    state = download_directory_from_ftp(ftp_connection, article, temp_dir)

    if state:
        article = article + '.zip'
        zip_name = item.provider.official_name
        # Create a temporary directory to store downloaded files
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        # Create a zip file from the downloaded content
        zip_filename = os.path.join(temp_dir, zip_name)
        zipped_file = shutil.make_archive(zip_filename.split('.')[0], 'zip', temp_dir)

        x = Archive.objects.filter(file_name_on_source=article)

        # if file not exists in database, create new record
        if not(x.exists()):
            # Save the zip file to the Django model
            with open(zipped_file, 'rb') as zip_file:
                zip_file.seek(0)
                # zip_file_model = ZipFileModel(name=zip_name)
                # zip_file_model.zip_file.save(zip_name + '.zip', ContentFile(zip_file.read()), save=True)

                x = Archive.objects.create(
                    file_name_on_source = article,
                    provider = item.provider,
                    processed_on = datetime.datetime.now(tz=pytz.utc),
                    status = 'active',
                    file_size = os.path.getsize(zipped_file),
                    file_type = '.zip'
                )

                article = str(x.id) + '.' + article.split('.')[-1]
                x.file_content.save(article, zip_file)

            # Cleanup temporary directory and return
            shutil.rmtree(temp_dir)
            return

        # if file exists than check the file size. If file size is different update the existing record
        if (x.exists() and not (x[0].file_size == os.path.getsize(zipped_file))):
            x[0].status = 'active'
            with open(zipped_file, 'rb') as zip_file:
                zip_file.seek(0)
                x[0].file_content.save(article, zip_file)

    print("zipped and exiting content")
            
    # Cleanup temporary directory
    shutil.rmtree(temp_dir)
    return



# this function will fetch article from the FTP
# @api_view(['GET'])
@login_required
@csrf_exempt
def download_from_ftp(request):
    err = []
    succ = []
    # get all providers that are due to be accessed
    due_for_download = Provider_meta_data_FTP.objects.filter(
        provider__next_due_date__lte = datetime.datetime.now(tz=pytz.utc)
        ).exclude(Q(protocol='SFTP') | Q(provider__in_production=False))
    
    print("total record to be executed", due_for_download.count())
    
    # if none is due to be accessed abort the process
    if not due_for_download.count():
        context = {
            'heading' : 'Message',
            'message' : 'No pending action found'
        }

        return render(request, 'common/dashboard.html', context=context)
        # return Response("No pending action found")

    # if providers are due to be accessed
    for item in due_for_download:
        print(item.server, item.account, item.pswd)
        err_occured = False
        err_msg = ''
        # try to ftp_connection to FTP, if error occures update the status to Provider_meta_data_FTP and continue to access next FTP
        try:
            ftp_connection =  ftplib.FTP()
            print("ftp object created")
            ftp_connection.connect(item.server, timeout=30)
            print("connected successfully")
            ftp_connection.login(item.account, item.pswd)
            print("logged in successfully")
            ftp_connection.set_pasv(True)
            print("passive mode enable")
            # read the destination location
            ftp_connection.cwd(item.site_path)
            print("changing path")
            article_library = ftp_connection.nlst()
            print("listing directories")
            succ.append(item.provider.official_name)
            print("appending list")
            # if record found explore inside.
            if article_library:
                # iterate through each file
                try:
                    print("trying to loo")
                    for article in article_library:
                        print("inside loop")
                        # check if the article is file or directory
                        if is_ftp_content_folder(ftp_connection, article):
                            print("inside loop => Processing directory")
                            # download the folder
                            download_folder_from_ftp_and_save_zip(ftp_connection, article, item)
                        else:
                            # download the file
                            print("inside loop => Processing file")
                            download_file(ftp_connection, article, item)

        
                    # update the succes status to Provider_meta_data_FTP
                    provider = item.provider
                    provider.last_time_received = datetime.datetime.now(tz=pytz.utc)
                    provider.status = 'success'
                    provider.next_due_date = datetime.datetime.now(tz=pytz.utc) + datetime.timedelta(item.provider.minimum_delivery_fq)

                    provider.save()

                    # quite the current ftp connection 
                    ftp_connection.quit()
                except Exception as e:
                    err_msg = e
                    print("error while processsing content", e)
                    err_occured = True

        except ftplib.error_temp as e:
            err_msg = e
            err_occured = True
            print(f"Temporary error: {e}")
        except ftplib.error_perm as e:
            err_msg = e
            err_occured = True
            print(f"Permanent error: {e}")
        except ftplib.error_proto as e:
            err_msg = e
            err_occured = True
            print(f"Protocol error: {e}")
        except ftplib.all_errors as e:
            err_msg = e
            err_occured = True
            print(f"FTP error: {e}")
        except socket.timeout as e:
            err_msg = e
            err_occured = True
            print(f"FTP error: {e}")

        if err_occured:
            provider = item.provider
            provider.status = 'failed'
            provider.last_error_message = err_msg
            provider.save()
            err.append(item.provider.official_name)



    context = {
        'heading' : 'Message',
        'message' : f'''FTP sync process executed successfully. Error occured in {err} and {succ} FTP's executed succesfully. The error is logged in the Provider model.'''
    }

    return render(request, 'common/dashboard.html', context=context)



