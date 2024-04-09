import requests

from step1.archive_article import Archived_article_attribute
from step1.providers import Provider_meta_data_API
from .common_for_api import save_in_db
import pytz
import datetime
import os
from html2text import html2text
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.files.base import ContentFile


# function to save the file
def save_files(response, api):
    # Retrieve file name and file size from response headers
    content_disposition = response.headers.get('content-disposition')
    if content_disposition:
        file_name = content_disposition.split('filename=')[1]
    else:
        file_name = (response.url).split('/')[-1] # Use URL as filename if content-disposition is not provided

    file_size = int(response.headers.get('content-length', 0))
    file_type = os.path.splitext(file_name)[1]

    # query to check if the same record exists
    qs = Archived_article_attribute.objects.filter(file_name_on_source=file_name)
    # if record exists and the size is also same, dont do anything
    if qs.exists() and qs[0].file_size == file_size:
        # finally update the last accessed success status
        return True

    # if record exists but the size is different, update the file
    elif qs.exists() and not qs[0].file_size == file_size:

        qs[0].file_size = file_size
        qs[0].file_content.save(file_name, ContentFile(response.content))
        return True

    else:
        x = Archived_article_attribute.objects.create(
            file_name_on_source = file_name,
            provider = api.provider,
            processed_on = datetime.datetime.now(tz=pytz.utc),
            status = 'success',
            file_size = file_size,
            file_type = file_type
        )

        # save file
        x.file_content.save(file_name, ContentFile(response.content))
        return True



# function to handle chorus ref api's
@api_view(['GET'])
def download_from_chorus_api(request):
    # Send a GET request to the URL.
    # query and fetch available submission api's
    qs = Provider_meta_data_API.objects.filter(api_meta_type="Chorus")

    for api in qs:
        response = requests.get(api.base_url)
        if response.status_code == 200:
            res = save_files(response, api)
            if res:
                api.last_pull_time = datetime.datetime.now(tz=pytz.utc)
                api.last_pull_status = 'success'
                api.last_error_message = 'N/A'
                api.save()
                return Response("processs executed successfully")

        api.last_pull_time = datetime.datetime.now(tz=pytz.utc)
        api.last_pull_status = 'failed'
        api.last_error_message = '=>// error code = error-code =' + str(response.status_code) + ' =>// error message = ' + html2text(response.text)
        api.save()
        return Response("processs executed with error")


