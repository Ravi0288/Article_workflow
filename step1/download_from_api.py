from django.http import HttpResponse
import os
from rest_framework.decorators import api_view
from .archive_article import Archived_article_attribute
from .archive_article import Archived_article_attribute
from .providers import Provider_meta_data_API
import datetime
import requests

from rest_framework.response import Response
import shutil
import os
from django.db.models import Q
import pytz
from .corus_api import *
from .crossref_api import *
from .submission_api import *


# Function to download folder and convert to zip.
def download_and_save_zip_using_api(folder_url, article, item):
    article = article + '.zip'
    zip_name = item.provider.official_name
    # Create a temporary directory to store downloaded files
    temp_dir = 'temp_download/' + item.provider.official_name
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
        zip_filename = os.path.join(temp_dir, zip_name)
        zipped_file = shutil.make_archive(zip_filename.split('.')[0], 'zip', temp_dir)

        x = Archived_article_attribute.objects.filter(file_name_on_source=article)

        # if file not exists in database, create new record
        if not(x.exists()):
            # Save the zip file to the Django model
            # with open(zip_filename, 'rb') as zip_file:
            qs = Archived_article_attribute.objects.create(
                file_name_on_source = article,
                provider = item.provider,
                processed_on = datetime.datetime.now(tz=pytz.utc),
                status = 'success',
                file_size = os.path.getsize(zipped_file),
                file_type = '.zip'
            )
            qs.file_content.save(article, zipped_file)
            
            # Cleanup temporary directory
            shutil.rmtree(temp_dir)
            return

        # if file exists than check the file size. If file size is different update the existing record
        if (x.exists() and not (x[0].file_size == os.path.getsize(zipped_file))):
            x[0].status = 'success'
            x[0].file_content.save(article, zipped_file)
            return

        # Cleanup temporary directory
        shutil.rmtree(temp_dir)
        
    return



@api_view(['GET'])
def download_from_api(request):
    # get all providers that are due to be accessed today
    due_for_download = Provider_meta_data_API.objects.filter(
        Q(next_due_date=datetime.datetime.now(tz=pytz.utc)) | 
        Q(last_pull_status="failed")
    )
    due_for_download = Provider_meta_data_API.objects.all()    
    # if none is due to be accessed abort the process
    if not due_for_download.count():
        return HttpResponse("No pending action found")

    for api in due_for_download:
        # if api.api_meta_type == 'CrossRef':
        #     download_from_crossref_api(api)
        # if api.api_meta_type == 'Chorus':
        #     download_from_chorus_api(api)
        if api.api_meta_type == 'Submission':
            download_from_submission_api(api)
    
    return Response("done")