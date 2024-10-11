import os
import datetime
import shutil
from io import BytesIO

import pysftp
import pytz
from django.shortcuts import render
from .archive import Archive
from .provider import Provider_meta_data_FTP
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from configurations.common import is_sftp_content_folder
from django.db.models import Q

# This function will download each file/dir from SFTP server to the local directory
# in case of given folder is blank or have any kind of error this will return False
def download_directory_from_sftp(sftp_connection, remote_directory, local_directory):
    if not os.path.exists(local_directory):
        os.makedirs(local_directory)

    content_list = sftp_connection.listdir(remote_directory)

    if len(content_list) == 0:
        return False
    
    try:
        for entry in content_list:
            remote_path = os.path.join(remote_directory, entry)
            local_path = os.path.join(local_directory, entry)
            
            if is_sftp_content_folder(sftp_connection, remote_path):
                download_directory_from_sftp(sftp_connection, remote_path, local_path)
            else:
                sftp_connection.get(remote_path, local_path)

        return True
    except Exception as e:
        print(e)
        return False


# Function to download a file
def download_file(sftp_connection, article, item):
    file_size = sftp_connection.stat(article).st_size
    # Check if record downloaded in our record and the file size is not zero
    x = Archive.objects.filter(file_name_on_source=article)

    # If file does not exist in the database, create a new record
    if not x.exists():
        content = BytesIO()
        sftp_connection.getfo(article, content)  # Using getfo to download file to BytesIO
        content.seek(0)
        file_type = os.path.splitext(article)[1]
        x = Archive.objects.create(
            file_name_on_source=article,
            provider=item.provider,
            processed_on=datetime.datetime.now(tz=pytz.utc),
            status='waiting',
            file_size=file_size,
            file_type=file_type
        )
        article = str(x.id) + '.' + article.split('.')[-1]
        x.file_content.save(article, content)
        return

    # If file exists, check the file size. If file size is different, update the existing record
    if x.exists() and not (x[0].file_size == file_size):
        content = BytesIO()
        sftp_connection.getfo(article, content)  # Using getfo to download file to BytesIO
        content.seek(0)
        x[0].status = 'active'
        x[0].is_content_changed = True
        article = str(x[0].id) + '.' + article.split('.')[-1]
        x[0].file_content.save(article, content)
        return


# Function to download folder with its content, convert to zip, and save to table
def download_folder_from_sftp_and_save_zip(sftp_connection, article, item):
    temp_dir = '/ai/metadata/' + item.provider.official_name
    state = download_directory_from_sftp(sftp_connection, article, temp_dir)

    if state:
        article = article + '.zip'
        zip_name = item.provider.official_name
        # Create a temporary directory to store downloaded files
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        # Assuming you have logic here to download folder contents to temp_dir
        # (You'll need to implement this based on your specific SFTP folder structure)

        # Create a zip file from the downloaded content
        zip_filename = os.path.join(temp_dir, zip_name)
        zipped_file = shutil.make_archive(zip_filename.split('.')[0], 'zip', temp_dir)

        x = Archive.objects.filter(file_name_on_source=article)

        # If file does not exist in the database, create a new record
        if not x.exists():
            # Save the zip file to the Django model
            with open(zipped_file, 'rb') as zip_file:
                zip_file.seek(0)
                x = Archive.objects.create(
                    file_name_on_source=article,
                    provider=item.provider,
                    processed_on=datetime.datetime.now(tz=pytz.utc),
                    status='active',
                    file_size=os.path.getsize(zipped_file),
                    file_type='.zip'
                )

                article = str(x.id) + '.' + article.split('.')[-1]
                x.file_content.save(article, zip_file)

            # Cleanup temporary directory and return
            shutil.rmtree(temp_dir)
            return

        # If file exists, check the file size. If file size is different, update the existing record
        if x.exists() and not (x[0].file_size == os.path.getsize(zipped_file)):
            x[0].status = 'active'
            with open(zipped_file, 'rb') as zip_file:
                zip_file.seek(0)
                x[0].file_content.save(article, zip_file)

    # Cleanup temporary directory
    shutil.rmtree(temp_dir)
    return


# This function will fetch articles from the SFTP
@login_required
@csrf_exempt
def download_from_sftp(request):
    err = []
    succ = []
    # Get all providers that are due to be accessed
    due_for_download = Provider_meta_data_FTP.objects.filter(
        provider__next_due_date__lte=datetime.datetime.now(tz=pytz.utc)
    ).exclude(Q(protocol='FTP') | Q(provider__in_production=False))

    # If none are due to be accessed, abort the process
    if not due_for_download.count():
        context = {
            'heading': 'Message',
            'message': 'No pending action found'
        }
        return render(request, 'common/dashboard.html', context=context)

    # If providers are due to be accessed
    for item in due_for_download:
        err_count = 0
        succ_count = 0
        # Try to connect to SFTP, if error occurs, update the status to Provider_meta_data_FTP
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        try:
            with pysftp.Connection(item.server, username=item.account, password=item.pswd, cnopts=cnopts) as sftp_connection:
                # Read the destination location
                sftp_connection.cwd(item.site_path)  # Change directory
                article_library = sftp_connection.listdir()  # List directory contents

                # If records found, explore inside.
                if article_library:
                    # Iterate through each file
                    for article in article_library:
                        try:
                            # Check if the article is a file or directory
                            if is_sftp_content_folder(sftp_connection, article):
                                # Download the folder
                                download_folder_from_sftp_and_save_zip(sftp_connection, article, item)
                            else:
                                # Download the file
                                download_file(sftp_connection, article, item)
                            succ_count += 1
                        except Exception as e:
                            print(f"Error processing article {article}: {e}")
                            err_count += 1

                # Update the success status in Provider_meta_data_FTP
                provider = item.provider
                provider.last_time_received = datetime.datetime.now(tz=pytz.utc)
                provider.status = 'success'
                provider.next_due_date = datetime.datetime.now(tz=pytz.utc) + datetime.timedelta(days=item.provider.minimum_delivery_fq)
                provider.save()
                provider.last_error_message = f''' {succ_count} files/directories saved successfully and error occured while saving {err_count} file/directories. '''
                succ.append(item.provider.official_name)

        except Exception as e:
            print("Error occurred:", e)
            provider = item.provider
            provider.status = 'failed'
            provider.last_error_message = str(e)
            provider.save()
            err.append(item.provider.official_name)
            continue

    context = {
        'heading': 'Message',
        'message': f'''SFTP sync process executed successfully. Error occured in {err} SFTP's while {succ} executed succesfully. The error is logged in the Provider model.'''
    }

    return render(request, 'common/dashboard.html', context=context)
