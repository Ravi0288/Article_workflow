import requests
from step1.archive import Archive
from step1.provider import Provider_meta_data_API
import pytz
import datetime
import os
import json
import sys
from io import BytesIO
from django.core.files import File
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from html2text import html2text
from django.views.decorators.csrf import csrf_exempt


# function to filter dataset
def filter_publisher_data(data):
    result = []
    for item in data:
        x = item['member_id']
        result.append(x)
    return result


def save_files(publishers, api, processed, created, updated, error_in_publishers):
    print("in save files function")
    for item in publishers:
        # access the url
        try:
            response = requests.get(f"https://api.chorusaccess.org/v1.1/agencies/{api.identifier_code}/publishers/{item}")
            response.raise_for_status()
        except requests.exceptions.SSLError as ssl_err:
            error_in_publishers += 1
            if "EOF occurred in violation of protocol" in str(ssl_err):
                print("SSL error: Unexpected EOF occurred in violation of protocol.")
            else:
                print(f"SSL error occurred: {ssl_err}")
            continue
        except requests.exceptions.Timeout:
            error_in_publishers += 1
            print(f"The request timed out.")
            continue
        except requests.exceptions.RequestException as e:
            error_in_publishers += 1
            print(f"An error occurred : {e}")
            continue
        
        if response.status_code == 200:
            data = response.json()
            if data.get('items', None):
                # iterate to each json object
                for content in data['items']:
                    processed += 1
                    doi = content['DOI']
                    # prepare properties
                    file_name = doi.replace('/','_').replace('//','_').replace('\\','_') + '.json'
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
                        fname = qs[0].file_content.path
                        # read the existing file
                        # Exception is added to ensure in case previous file is corrupt or deleted the freash file will be updated
                        try:
                            f = open(fname, 'r')
                            jsonified_content = json.load(f)
                            f.close()
                        except Exception as e:
                            jsonified_content = {}

                        # compare the contents
                        if jsonified_content == content:
                            continue
                        else:
                            # if existing content differs with received content, than
                            # remove the exisitng file and update the record
                            try:
                                os.remove(fname)
                            except:
                                pass
                            # save file
                            qs[0].file_size = file_size
                            qs[0].status = "waiting"
                            qs[0].is_content_changed = True
                            file_name = str(qs[0].id) + '.json'
                            qs[0].file_content.save(file_name, _file)
                            updated += 1

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
                        file_name = str(x.id) + '.json'
                        x.file_content.save(file_name, _file)
                        created += 1

    
    return processed, created, updated, error_in_publishers



# function to handle chorus ref api's
# @api_view(['GET'])
@login_required
@csrf_exempt
def download_from_chorus_api_old(request):
    err = []
    succ = []
    publisher = []
    processed = created = updated = error_in_publishers = 0
    # query and fetch available chorus api's
    due_for_download = Provider_meta_data_API.objects.filter(
        api_meta_type="Chorus", provider__next_due_date__lte = datetime.datetime.now(tz=pytz.utc)
        ).exclude(provider__in_production=False)

    # iterate to all the available chorus apis
    for api in due_for_download:
        headers= {
            'Content-type' : 'json',
            'Authorization': f'''Bearer {api.site_token}'''
        }

        try:
            response = requests.get(
                f"https://api.chorusaccess.org/v1.1/agencies/{api.identifier_code}/publishers/",
                headers=headers
                )
        except Exception as e:
            print(e, "Error occured while requesting https://api.chorusaccess.org/v1.1/agencies/api.identifier_code/publishers/ url")
        
        if response.status_code == 200:
            data = response.json()
            print("response 200 and response converted to json")
            if response.status_code == 200 and len(data):
                publisher.extend(filter_publisher_data(data['publishers']))
            print("publishers list extended")
            if len(publisher):
                print("publishers found")
                processed, created, updated, error_in_publishers = save_files(publisher, api, processed, created, updated, error_in_publishers)
                print("data saved successfully")

            print("updating api")
            provider = api.provider
            provider.last_time_received = datetime.datetime.now(tz=pytz.utc)
            provider.status = 'success'
            provider.last_error_message = 'N/A'
            provider.save()
            succ.append(api.provider.working_name)
            print("api updated successfully")

        else:
            print("error occured", response.status_code)
            provider = api.provider
            provider.status = 'failed'
            provider.last_error_message = 'error code =' + str(response.status_code) + ' and error message = ' + html2text(response.text)
            provider.save()
            err.append(api.provider.working_name)
            print("api updated with failed status")

    if err:
        context = {
            'heading' : 'Message',
            'message' : f'''Chorus API exited with error. Error message: {err}'''
        }

    elif succ:
        unchanged = processed - (created - updated)
        total_publishers = len(publisher)
        context = {
            'heading' : 'Message',
            'message' : f'''Chorus API synced successfully. 
                        Total {processed} record found, 
                        {created} new records created, 
                        {updated} records updated. {unchanged} records either found unchanged or skipped. 
                        {total_publishers} publishers found and Error occurred in {error_in_publishers} publishers while fetching data.'''
        }

    else:
        context = {
            'heading' : 'Message',
            'message' : 'Chorus API synced successfully. No pending Chorus API found to sync.'
        }

    return render(request, 'common/dashboard.html', context=context)
