from django.conf import settings
from django.shortcuts import render
from html2text import html2text
import requests
from step1.archive import Archive

from step1.provider import Provider_meta_data_API
import pytz
import datetime
import os
from django.core.files.base import ContentFile
import zipfile
import json
import sys
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import certifi


# Function to retrieve a list of DOIs for articles from a given journal by ISSN
def get_article_dois_by_issn(issn, api, request, num_rows=1000):
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
        provider = api.provider
        provider.status = 'failed'
        provider.last_error_message = 'error code =' + str(response.status_code) + ' and error message = ' + html2text(response.text)
        provider.save()
        # api.save()
        # return Response("error occured")


    context = {
        'heading' : 'Message',
        'message' : 'CrossRef API process executed successfully'
    }

    return render(request, 'common/dashboard.html', context=context)

# function to zip folder
def zip_folder(folder_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
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
    

def save_files(dois, headers, api):
    state = True
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    # i=0
    for doi in dois:
        # setting url parameters
        params = dict(version='1.2', operation='searchRetrieve', startRecord=0,
                        maximumRecords=1000,
                        query='alma.local_field_918=crossref and alma.local_notes="PubAg Journal"')

        # access the url
        url = f"https://api.crossref.org/works/{doi}"
        response = requests.get(url, params=params, headers=headers, verify=certifi.where())
        # response = requests.get(url)
        # response = http.request("GET", f"https://api.crossref.org/works/{doi}", body=params, headers=headers)
        if response.status_code == 200:
            try:
                # prepare properties
                file_name = doi.replace('/', '_') + '.json'
                file_type = '.json'
                data = response.json()

                # check if record against same doi exists
                qs = Archive.objects.filter(unique_key=doi)
                if qs.exists():
                    # if record exists, compare existing content with received content.
                    # if existing content == received content do nothing
                    doi = doi.replace('/', '_')
                    # fname = os.path.join(settings.CROSSREF_ROOT, doi + '.json')
                    fname = os.path.join(settings.MEDIA_ROOT, qs[0].file_content.name)
                    
                    # read the existing files
                    f = open(fname, 'r')
                    jsonified_content = json.load(f)
                    f.close()

                    # compare the contents
                    if jsonified_content == data:
                        pass
                    else:
                        # if existing content differs with received content, remove the exisitng file an update the record
                        os.remove(fname)
                        file_size = sys.getsizeof(response.json())
                        # save file
                        qs[0].file_size = file_size
                        qs[0].status = "waiting"
                        qs[0].is_content_changed = True
                        file_name = str(x.id) + '.' + qs[0].split('.')[-1]
                        qs[0].file_content.save(file_name, ContentFile(response.content))

                else:
                    # Getting size using getsizeof() method
                    file_size = sys.getsizeof(response.json())
                    x = Archive.objects.create(
                        file_name_on_source = file_name,
                        provider = api.provider,
                        processed_on = datetime.datetime.now(tz=pytz.utc),
                        status = 'waiting',
                        file_size = file_size,
                        file_type = file_type,
                        unique_key = doi
                    )

                    # save file
                    file_name = str(x.id) + '.' + file_name.split('.')[-1]
                    x.file_content.save(file_name, ContentFile(response.content))

            except Exception as e:
                print(e)
                continue
        else:
            x = (response.__dict__)
            print("Response code:", response.status_code,", reason :", response.reason)

    # zip the file
    # path = os.path.join(settings.CROSSREF_ROOT , current_date + '.zip')
    # zip_folder(settings.CROSSREF_ROOT, path)




# function to handle all the crossref api's
# @api_view(['GET'])
@login_required
@csrf_exempt
def download_from_crossref_api(request):

    # receive the issn_number
    issn_number = request.GET.get('issn_number')

    # if issn_number not received, assign default
    if not issn_number:
        issn_number = "0066-4804"

    # query and fetch available submission api's
    due_for_download = Provider_meta_data_API.objects.filter(
        api_meta_type="CrossRef", provider__next_due_date__lte = datetime.datetime.now(tz=pytz.utc)
        ).exclude(provider__in_production=False)
    
    # iterate through each records found
    for api in due_for_download:

        # set request header
        headers = {
            'Crossref-Plus-API-Token': 'Bearer {}'.format(api.pswd),
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/999.0.9999.999 Safari/537.36'
            }

        # get list of doi
        article_dois = get_article_dois_by_issn(issn=issn_number, api=api, request=request)

        # as per received dois make urls and downloaded the file in json format
        save_files(article_dois, headers, api)

        # update the last run status
        provider = api.provider
        provider.last_time_received = datetime.datetime.now(tz=pytz.utc)
        provider.status = 'success'
        provider.last_error_message = 'N/A'
        provider.save()
        # api.save()
    # return Response("success")

    context = {
        'heading' : 'Message',
        'message' : 'CrossRef API process executed successfully'
    }

    return render(request, 'common/dashboard.html', context=context)