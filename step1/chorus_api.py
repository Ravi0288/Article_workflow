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



# function to compate to given date
def compare_date(updated_date, fetched_date):
    updated_date = datetime.datetime.strptime(updated_date, "%d/%m/%Y")
    # Parse date_received_date (format: yyyy-mm-dd HH:MM:SS.ssssss+zz:zz)
    fetched_date = datetime.datetime.strptime(str(fetched_date), "%Y-%m-%d %H:%M:%S.%f%z")
    fetched_date = fetched_date.replace(tzinfo=None)
    if updated_date < fetched_date:
        return True
    else:
        return


# function to create / update the json objects
def save_files(data, api, processed, created, updated, error_in_publishers):
    for content in data:
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
            # try:
            #     f = open(fname, 'r')
            #     jsonified_content = json.load(f)
            #     f.close()
            # except Exception as e:
            #     jsonified_content = {}

            date_received = qs[0].received_on
            updated_dt = content.get('updated', None)
            if not updated_dt:
                print("date not found in", qs[0].id)
            if updated_dt and compare_date(updated_dt, date_received):
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
def download_from_chorus_api(request):
    err = []
    succ = []
    publisher = []
    processed = 0
    created = 0
    updated = 0
    error_in_publishers = 0

    # query and fetch available chorus api's
    due_for_download = Provider_meta_data_API.objects.filter(
        api_meta_type="Chorus", provider__next_due_date__lte = datetime.datetime.now(tz=pytz.utc)
        ).exclude(provider__in_production=False)

    per_page = 100
    start_from_page = 0
    # iterate to all the available chorus apis
    for api in due_for_download:
        headers= {
            'Content-type' : 'application/vnd.api+json',
            'Authorization': f'''Bearer {api.site_token}'''
        }

        # this code is written as per existing logic.
        try:
            while True:
                # set value to fetch pages per request with per_page that is the max limit of page in every single request
                # offset means how many pages to skip and than start counting the page. This value will be update on every request
                params = {
                    "limit" : per_page,
                    "offset" : per_page * start_from_page
                }

                response = requests.get(
                    f"https://api.chorusaccess.org/v1.1/agencies/{api.identifier_code}/histories/current",
                    headers=headers,
                    params=params
                    )
                    
                if response.status_code == 200:
                    data = response.json()
                    data=data.get('items', None)

                    # if data received prepare to fetch next record
                    if data:
                        start_from_page += 1
                    else:
                        # if no data received break the loop
                        break

                    processed, created, updated, error_in_publishers = save_files(data, api, processed, created, updated, error_in_publishers)
            
                else:
                    print("error", response.status_code)
                    # break # enable this break statement to exit immediately incase error occures.

            provider = api.provider
            provider.last_time_received = datetime.datetime.now(tz=pytz.utc)
            provider.status = 'success'
            provider.last_error_message = 'N/A'
            provider.save()
            succ.append(api.provider.working_name)

        except Exception as e:
            provider = api.provider
            provider.status = 'dropped'
            provider.last_error_message = e
            provider.save()
            err.append(api.provider.working_name)

    if err:
        context = {
            'heading' : 'Message',
            'message' : f'''Chorus API exited with error. Error message: {provider.last_error_message}'''
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
