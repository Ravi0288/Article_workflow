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
def get_article_dois_by_funder_id(funder_id, api, num_rows=1000):
    dois = []

    # Make a GET request to the CrossRef journals endpoint
    response = requests.get(
        f"https://api.crossref.org/funders/{funder_id}//works?filter=has-abstract:true", 
        params={"rows": num_rows, "cursor": '*'}
        )

    # Make a GET request to the CrossRef journals endpoint
    # response = requests.get(f"https://api.crossref.org/journals/{funder_id}/works", params={"rows": num_rows})
    if response.status_code == 200:
        data = response.json()
        # Extract DOIs from the response JSON
        items = data.get("message", {}).get("items", [])
        for item in items:
            doi = item.get("DOI")
            try:
                if doi:
                    dois.append(doi)
            except Exception as e:
                print(e)

    else:
        provider = api.provider
        provider.status = 'failed'
        provider.last_error_message = 'error code =' + str(response.status_code) + ' and error message = ' + html2text(response.text)
        provider.save()

    return dois

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
    

def save_files(dois, api):

    updated = 0
    created = 0
    err = 0

    # # set request header
    # headers = {
    #     'Crossref-Plus-API-Token': 'Bearer {}'.format(api.pswd),
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/999.0.9999.999 Safari/537.36'
    #     }

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Crossref-Plus-API-Token': f'Bearer {api.pswd}'
    }

    # setting url parameters
    params = {
        'version' : '1.2', 
        'operation' : 'searchRetrieve', 
        'startRecord'  : 0,
        'maximumRecords' : 1000,
        'query' : 'alma.local_field_918=crossref and alma.local_notes="PubAg Journal"'
    }

    for doi in dois:
        # access the url
        url = f'''https://api.crossref.org/works/{doi}'''

        try:
            # response = requests.get(url, params=params, headers=headers, verify=certifi.where())
            response = requests.get(url, headers=headers, verify=certifi.where(), timeout=10)
            # response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.SSLError as ssl_err:
            if "EOF occurred in violation of protocol" in str(ssl_err):
                print("SSL error: Unexpected EOF occurred in violation of protocol.")
            else:
                print(f"SSL error occurred: {ssl_err}")
            continue
        except requests.exceptions.Timeout:
            print(f"The request timed out after")
            continue
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            continue


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
                    fname = qs[0].file_content.path
                    
                    # read the existing files
                    f = open(fname, 'r')
                    jsonified_content = json.load(f)
                    f.close()

                    # compare the contents, If content are unchanged pass
                    if jsonified_content == data:
                        pass

                    # if content found changed, update the record
                    else:
                        # if existing content differs with received content, remove the exisitng file and update the record
                        os.remove(fname)
                        file_size = sys.getsizeof(response.json())
                        # save file
                        qs[0].file_size = file_size
                        qs[0].status = "waiting"
                        qs[0].is_content_changed = True
                        qs[0].file_content.save(qs[0].file_content.name, ContentFile(response.content))

                        updated += 1

                else:
                    # Getting size using getsizeof() method
                    file_size = sys.getsizeof(response.json())
                    qs = Archive.objects.create(
                        file_name_on_source = file_name,
                        provider = api.provider,
                        processed_on = datetime.datetime.now(tz=pytz.utc),
                        status = 'waiting',
                        file_size = file_size,
                        file_type = file_type,
                        unique_key = doi
                    )

                    # save file
                    file_name = str(qs.id) + '.' + file_name.split('.')[-1]
                    qs.file_content.save(file_name, ContentFile(response.content))

                    created += 1

            except Exception as e:
                print(e)
                err += 1
        else:
            print("Response code:", response.status_code,", reason :", response.reason)
            err += 1
    return created, updated, err



# function to handle all the crossref api's
# @api_view(['GET'])
@login_required
@csrf_exempt
def download_from_crossref_api(request):

    context = {
        'heading' : 'Message',
        'message' : 'CrossRef API process executed successfully'
    }

    # query and fetch available submission api's
    due_for_download = Provider_meta_data_API.objects.filter(
        api_meta_type="CrossRef", provider__next_due_date__lte = datetime.datetime.now(tz=pytz.utc)
        ).exclude(provider__in_production=False)
    
    # if crossref is not due to access, return response
    if not due_for_download.count():
        context['message'] = f'''No Pending action found for CrossRef.'''
        return render(request, 'common/dashboard.html', context=context)


    # iterate through each records found
    rec_count = 0
    for api in due_for_download:
        funder_id = api.identifier_code

        # get list of doi
        article_dois = get_article_dois_by_funder_id(funder_id=funder_id, api=api)

        if len(article_dois):
            # as per received dois make urls and download the file in json format
            created, updated, err = save_files(article_dois, api)
            rec_count += len(article_dois)

        # update the last run status
        provider = api.provider
        provider.last_time_received = datetime.datetime.now(tz=pytz.utc)
        provider.status = 'success'
        provider.last_error_message = 'N/A'
        provider.save()

    skipped = rec_count - (created + updated)
    if rec_count:
        context['message'] = f'''CrossRef API process executed successfully. 
                                Total {rec_count} records found
                                and {created} created, {updated} updated successfully while {err} records ended with error. 
                                {skipped} records skipped because they are same as in our archive.
                                '''
    else:
        context['message'] = f'''CrossRef API process executed successfully. No records found to update / create.'''

    return render(request, 'common/dashboard.html', context=context)