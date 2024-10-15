import requests

from step1.archive import Archive
from step1.provider import Provider_meta_data_API
import pytz
import datetime
import os
from django.conf import settings
import json
import sys
from io import BytesIO
from django.core.files import File
import zipfile
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from html2text import html2text
from django.views.decorators.csrf import csrf_exempt


# function to zip folder with content
def zip_folder(folder_path):
    zip_file_path = f"{folder_path}.zip"
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)

# function to iterate through each folder inside folder and call zip_function
def zip_folders(root_folder):
    for root, dirs, files in os.walk(root_folder):
        for dir_name in dirs:
            folder_path = os.path.join(root, dir_name)
            zip_folder(folder_path)



# function to filter dataset
def filter_publisher_data(data):
    result = []
    for item in data:
        x = item['member_id']
        # obj = {
        #     'content-type' : item['link'][0]['content-type'],
        #     'url' : item['link'][0]['URL']
        # }
        result.append(x)
    return result


def save_files(publishers,api):
    state = True
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    publishers = [12,13]
    for item in publishers:
        # access the url
        # response = requests.get(url['url'],params=params, headers=headers)
        response = requests.get(f"https://api.chorusaccess.org/v1.1/agencies/{api.identifier_code}/publishers/{item}")
        if response.status_code == 200:
            data = response.json()
            if data.get('items', None):
                # iterate to each json object
                # i=0
                for content in data['items']:
                    # i=+1
                    # if(i>2):
                    #     break
                    doi = content['DOI']
                    # prepare properties
                    file_name = os.path.join(str(item), doi.replace('/','_') + '.json')
                    file_type = '.json'
                    file_size = sys.getsizeof(content)
                    # Serialize JSON object to a string
                    json_string = json.dumps(content)

                    # Convert string to BytesIO object
                    json_bytes = BytesIO(json_string.encode())

                    # Create a Django File object
                    _file = File(json_bytes)

                    # check if record against same doi exists
                    qs = Archive.objects.filter(unique_key=doi)
                    if qs.exists():
                        # if record exists, compare existing content with received content.
                        # if existing content == received content do nothing
                        # fname = os.path.join(settings.CHORUS_ROOT, file_name)
                        fname = os.path.join(settings.ARCHIVE_ROOT, qs[0].file_content.name)
                        
                        # read the existing file
                        f = open(fname, 'r')
                        jsonified_content = json.load(f)
                        f.close()

                        # compare the contents
                        if jsonified_content == content:
                            continue
                        else:
                            # if existing content differs with received content, than
                            # remove the exisitng file and update the record
                            os.remove(fname)
                            # save file
                            qs[0].file_size = file_size
                            qs[0].status = "waiting"
                            qs[0].is_content_changed = True
                            file_name = str(qs[0].id) + '.' + file_name.split('.')[-1]
                            qs[0].file_content.save(file_name, _file)

                    else:
                        # Getting size using getsizeof() method
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
                        x.file_content.save(file_name, _file)

    
    return True



# function to handle chorus ref api's
# @api_view(['GET'])
@login_required
@csrf_exempt
def download_from_chorus_api(request):
    err = []
    succ = []
    publisher = []
    # Send a GET request to the URL.
    # query and fetch available submission api's
    due_for_download = Provider_meta_data_API.objects.filter(
        api_meta_type="Chorus", provider__next_due_date__lte = datetime.datetime.now(tz=pytz.utc)
        )
    per_page = 100
    start_from_page = 0
    headers= {
        'Content-type' : 'json'
    }
    # iterate to all the available chorus apis
    for api in due_for_download:
        # # this code is written as per existing logic.
        # while True:
        #     params = {
        #         "limit" : per_page,
        #         "offset" : per_page * start_from_page
        #     }

        #     response = requests.get(
        #         f"https://api.chorusaccess.org/v1.1/agencies/{api.identifier_code}/histories/current",
        #         headers=headers,
        #         params=params
        #         )
        #     data = response.json()
        #     print(len(data))
        #     if response.status_code == 200 and len(data):
        #         publisher.extend(filter_publisher_data(data['publishers']))
        #         start_from_page += 1
        #     else:
        #         break

        response = requests.get(
            f"https://api.chorusaccess.org/v1.1/agencies/{api.identifier_code}/publishers/",
            headers=headers
            )
        
        if response.status_code == 200:
            data = response.json()
            if response.status_code == 200 and len(data):
                publisher.extend(filter_publisher_data(data['publishers']))

            if len(publisher):
                save_files(publisher, api)

            provider = api.provider
            provider.last_time_received = datetime.datetime.now(tz=pytz.utc)
            provider.status = 'success'
            provider.last_error_message = 'N/A'
            provider.save()
            succ.append(api.provider.official_name)

        else:
            provider = api.provider
            provider.status = 'failed'
            provider.last_error_message = 'error code =' + str(response.status_code) + ' and error message = ' + html2text(response.text)
            provider.save()
            err.append(api.provider.official_name)

            print(provider.last_error_message)



    # return Response("processs executed successfully")
    if err:
        context = {
            'heading' : 'Message',
            'message' : f'''Chorus API exited with error. Error message: {provider.last_error_message}'''
        }

    elif succ:
        context = {
            'heading' : 'Message',
            'message' : f'''Chorus API process executed successfully. Total {len(publisher)} record saved.'''
        }

    else:
        context = {
            'heading' : 'Message',
            'message' : 'Chorus API process executed successfully. No pending chorus api action found'
        }

    return render(request, 'common/dashboard.html', context=context)
