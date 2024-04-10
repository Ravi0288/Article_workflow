from django.conf import settings
from html2text import html2text
import requests
import urllib3
from step1.archive_article import Archived_article_attribute

from step1.providers import Provider_meta_data_API
from .common_for_api import save_in_db
from django.http import HttpResponse
import pytz
import datetime
import os
from rest_framework.decorators import api_view
from django.core.files.base import ContentFile
import zipfile



# Function to retrieve a list of DOIs for articles from a given journal by ISSN
def get_article_dois_by_issn(issn, num_rows=10):
    dois = []
    # Make a GET request to the CrossRef journals endpoint
    response = requests.get(f"https://api.crossref.org/journals/{issn}/works", params={"rows": num_rows})
    if response.status_code == 200:
        data = response.json()
        # Extract DOIs from the response JSON
        items = data.get("message", {}).get("items", [])
        for item in items:
            doi = item.get("DOI")
            if doi:
                dois.append(doi)
    return dois

# Function to retrieve metadata for each article given a DOI
def get_article_metadata(doi):
    metadata = {}
    # Make a GET request to the CrossRef works endpoint
    response = requests.get(f"https://api.crossref.org/works/{doi}")
    if response.status_code == 200:
        data = response.json()
        # Extract metadata from the response JSON
        metadata["title"] = data.get("message", {}).get("title", "")
        metadata["authors"] = [author.get("given", "") + " " + author.get("family", "") for author in data.get("message", {}).get("author", [])]
        # Add more metadata fields as needed
    return metadata



# function to zip folder
def zip_folder(folder_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.abspath(folder_path))
                zipf.write(file_path, arcname)


# function to filter dataset
def filter_data(data):
    result = []
    data = data['message']['items']
    # iterate through the data
    for item in data:
        obj = {
            'content-type' : item['link'][0]['content-type'],
            'url' : item['link'][0]['URL']
        }
        result.append(obj)
    return result
    

def save_files(urls, headers, api):
    state = True
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    for url in urls:
        params = dict(version='1.2', operation='searchRetrieve', startRecord=0,
                        maximumRecords=1000,
                        query='alma.local_field_918=crossref and alma.local_notes="PubAg Journal"')

        response = requests.get(url['url'],params=params, headers=headers)
        if response.status_code == 200:
            # Retrieve file name and file size from response headers
            content_disposition = response.headers.get('content-disposition')
            if content_disposition:
                file_name = current_date + '/' + content_disposition.split('filename=')[1]
            else:
                file_name = current_date + '/' + (response.url).split('/')[-1] # Use URL as filename if content-disposition is not provided
            
            file_size = int(response.headers.get('content-length', 0))
            file_type = url['content-type']


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
        else:
            print(response.status_code, "##############")
    try:
        folder_path = 'article_library/CROSSREF/' + current_date
        zip_folder(folder_path, folder_path + '.zip')
    except Exception as e:
        print(e)
    
    return True





# function to handle all the crossref api's
@api_view(['GET'])
def download_from_crossref_api(request):
    # maintain state to true, in case any error occures this should be changed to false
    # state = True
    # query and fetch available submission api's
    qs = Provider_meta_data_API.objects.filter(api_meta_type="CrossRef")

    # set request header
    #  'Crossref-Plus-API-Token': 'Bearer {}'.format(api.pswd),
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'
        }
    
    # iterate through each records found
    for api in qs:

        # get from website
        response = requests.get(
            "https://api.crossref.org/journals/0066-4804/works?rows=1000",
            verify=False
        )

        if(response.status_code == 200):
            state = save_files(filter_data(response.json()), headers, api)
            api.last_pull_time = datetime.datetime.now(tz=pytz.utc)
            api.last_pull_status = 'success'
            api.last_error_message = 'N/A'
            api.save()
            return HttpResponse("success")
        else:
            api.last_pull_time = datetime.datetime.now(tz=pytz.utc)
            api.last_pull_status = 'success'
            api.last_error_message = '=>// error code = error-code =' + str(response.status_code) + ' =>// error message = ' + html2text(response.text)
            api.save()
            return HttpResponse("error")

