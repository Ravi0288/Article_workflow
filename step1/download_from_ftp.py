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


# Funciton to parse the information collected from FTP for each files
def parse_file_info_of_files_on_ftp(attr):
    # Parse a single line from MLSD response
    facts = {}
    segments = attr.split(';')
    for segment in segments[:-1]:
        key, value = segment.split('=')
        facts[key.lower()] = value
    facts['name'] = segments[-1].strip()
    return facts


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
        x[0].status = 'waiting'
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
        
        err_occurred = False
        err_msg = ''
        err_count = 0
        succ_count = 0
        # try to ftp_connection to FTP, if error occures update the status to Provider_meta_data_FTP and continue to access next FTP
        try:
            ftp_connection = ftplib.FTP()
            ftp_connection.set_debuglevel(0)
            ftp_connection.connect(item.server, timeout=60)
            ftp_connection.login(item.account, item.pswd)
            ftp_connection.set_pasv(True)
            # read the destination location
            ftp_connection.cwd(item.site_path)
            # article_library = ftp_connection.nlst()
            
            '''
            preprocess the list of files to be downloaded.
            compare the files and their size, filter out all the files that are already downloaded and flag those who have modified
            '''
            # make list of file attributes
            attrs = []
            article_library = []
            ftp_connection.retrlines('MLSD', attrs.append)
            print("MLSD executed")
            # iterate each lines and filter required files
            for attr in attrs:
                print(attr)
                facts = parse_file_info_of_files_on_ftp(attr)
                file_name = facts['name']
                file_size = int(facts.get('size', 0))
                last_modified = facts.get('modify', '')
                try:
                    last_modified = datetime.datetime.strptime(last_modified, '%Y%m%d%H%M%S')
                    last_modified = last_modified.replace(tzinfo=datetime.timezone.utc)
                except:
                    last_modified = 0

                try:
                    if last_modified:
                        Archive.objects.get(file_name_on_source = file_name, received_on__lt = last_modified)
                    else:
                        Archive.objects.get(file_name_on_source = file_name, file_size=file_size)
                    print("found")
                except Archive.DoesNotExist:
                    article_library.append(file_name)

            # Showing list of successfull providers for view purpose
            succ.append(item.provider.official_name)

            # if files found than start download
            print(f''' Total {len(article_library)} to be downloaded''')
            if article_library:
                # iterate through each file
                for article in article_library:
                    try:
                        # check if the article is file or directory
                        if is_ftp_content_folder(ftp_connection, article):
                            # download the folder
                            download_folder_from_ftp_and_save_zip(ftp_connection, article, item)
                        else:
                            # download the file
                            download_file(ftp_connection, article, item)

                        succ_count += 1 

                    except Exception as e:
                        err_count += 1
                        print("error while processsing content", e)
                        pass
        
                # update the succes status to Provider_meta_data_FTP
                provider = item.provider
                provider.last_time_received = datetime.datetime.now(tz=pytz.utc)
                provider.status = 'success'
                provider.next_due_date = datetime.datetime.now(tz=pytz.utc) + datetime.timedelta(item.provider.minimum_delivery_fq)
                provider.last_error_message = f''' {succ_count} files/directories saved successfully and error occurred while saving {err_count} file/directories. '''
                provider.save()

                # quite the current ftp connection 
                ftp_connection.quit()


        except ftplib.error_temp as e:
            err_msg = e
            err_occurred = True
            print(f"Temporary error: {e}")
        except ftplib.error_perm as e:
            err_msg = e
            err_occurred = True
            print(f"Permanent error: {e}")
        except ftplib.error_proto as e:
            err_msg = e
            err_occurred = True
            print(f"Protocol error: {e}")
        except ftplib.all_errors as e:
            err_msg = e
            err_occurred = True
            print(f"FTP error: {e}")
        except socket.timeout as e:
            err_msg = e
            err_occurred = True
            print(f"FTP error: {e}")

        if err_occurred:
            provider = item.provider
            provider.status = 'failed'
            provider.last_error_message = err_msg
            provider.save()
            err.append(item.provider.official_name)



    context = {
        'heading' : 'Message',
        'message' : f'''FTP sync process executed successfully. Error occurred in {err} and {succ} FTP's executed successfully. The error is logged in the Provider model.'''
    }

    return render(request, 'common/dashboard.html', context=context)