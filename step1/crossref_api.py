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
from rest_framework.response import Response



# Function to retrieve a list of DOIs for articles from a given journal by ISSN
def get_article_dois_by_issn(issn, api, num_rows=1000):
    dois = []
    # Make a GET request to the CrossRef journals endpoint
    response = requests.get(f"https://api.crossref.org/journals/{issn}/works", params={"rows": num_rows})
    if response.status_code == 200:
        data = response.json()
        # Extract DOIs from the response JSON
        items = data.get("message", {}).get("items", [])
        for item in items:
            doi = item.get("DOI")
            try:
                if doi:
                    dois.append(doi)
                    # print(item['message']['items']['link'][0]['URL'], "#################",doi)
            except Exception as e:
                print(e)
        return dois
    else:
        api.last_pull_time = datetime.datetime.now(tz=pytz.utc)
        api.last_pull_status = 'success'
        api.last_error_message = '=>// error code = error-code =' + str(response.status_code) + ' =>// error message = ' + html2text(response.text)
        api.save()
        return Response("error occured")

# Function to retrieve metadata for each article given a DOI
def get_article_metadata(api,doi):

    # Make a GET request to the CrossRef works endpoint
    response = requests.get(f"https://api.crossref.org/works/{doi}")

    # if gets succes response 
    if response.status_code == 200:
        data = response.json()

        # check if record against same doi exists
        qs = Archived_article_attribute.objects.filter(unique_key=doi)
        if qs.exists():
            # if record exists, compare existing content with received content.
            # if existing content == received content do nothing
            if qs[0].jsonified_content == data:
                print("no data change")
                return True
            else:
                # if existing content differs with received content update the record
                qs[0].jsonified_content = data
                qs[0].save()
                print("data change found")
                return True

        else:
            # in case of new record perform create operation
            print("creating fresh record")
            Archived_article_attribute.objects.create(
                file_name_on_source = "N/A",
                provider = api.provider,
                processed_on = datetime.datetime.now(tz=pytz.utc),
                status = 'success',
                file_size = 0,
                file_type = "N/A",
                jsonified_content = data,
                unique_key = doi
                )
    return True



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

    issn_number = request.GET.get('issn_number')

    # if issn_number not received, assign default
    if not issn_number:
        issn_number = "0066-4804"
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
        # Replace with the ISSN of the desired journal
        article_dois = get_article_dois_by_issn(issn=issn_number, api=api)
        i = 1
        for doi in article_dois:
            print(i, "##")
            get_article_metadata(api, doi)
            i+=1
            # state = save_files(filter_data(response.json()), headers, api)
        api.last_pull_time = datetime.datetime.now(tz=pytz.utc)
        api.last_pull_status = 'success'
        api.last_error_message = 'N/A'
        api.save()
        return HttpResponse("success")


