from html2text import html2text
import requests
from .common_for_api import save_in_db
from django.http import HttpResponse
import pytz
import datetime
import os

# function to handle all the crossref api's
def download_from_crossref_api(api):
    # Send a GET request to the URL.
    headers = {'Authorization': "Bearer {}".format(api.pswd)}
    response = requests.get(
        api.base_url,
        headers=headers,
        verify=False
    )

    if response.status_code == 200:
        # Retrieve file name and file size from response headers
        content_disposition = response.headers.get('content-disposition')
        if content_disposition:
            file_name = 'crossref/' + content_disposition.split('filename=')[1]
        else:
            file_name = 'crossref/' + (response.url).split('/')[-1] # Use URL as filename if content-disposition is not provided
        
        file_size = int(response.headers.get('content-length', 0))
        file_type = os.path.splitext(file_name)[1]

        save_in_db(api, file_name, file_size, file_type, response)

    else:
        api.last_pull_time = datetime.datetime.now(tz=pytz.utc)
        api.last_pull_status = 'failed'
        api.last_error_message = '=>// error code = error-code =' + str(response.status_code) + ' =>// error message = ' + html2text(response.text)
        api.save()
        

    return HttpResponse("done")

