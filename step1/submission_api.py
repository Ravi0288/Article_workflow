from html2text import html2text
import requests

from step1.archive import Archive
from step1.provider import Provider_meta_data_API
from django.http import HttpResponse
import pytz
import datetime
import os
from rest_framework.decorators import api_view
from django.core.files.base import ContentFile
import json
from django.conf import settings
import zipfile
from rest_framework.response import Response


# function to zip folder
def zip_folder(folder_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.abspath(folder_path))
                zipf.write(file_path, arcname)



# class to download file from the api
class SubmissionMetadataHarvester:
    def __init__(self, base_url):
        self.base_url = base_url

    # this function will download the file till gets {} as response
    def fetch_submissions(self, last_date):
        page = 0
        all_submission = []

        while True:
            try:
                url = self.base_url.format(page, "2023-02-02")
            except Exception as e:
                print(e)

            try:
                response = requests.get(url)
            except Exception as e:
                print(e)

            # if status code is not success exit
            if response.status_code != 200:
                print("response code", response.status_code)
                break

            # if nil data received exit the loop
            if len(response.json()) == 0:
                break

            # if data received append data to list
            submissions = response.json()
            all_submission.extend(submissions)

            # increase the page number
            page += 1

        return all_submission
    

# function to handle submission api's
@api_view(['GET'])
def download_from_submission_api(request):
    # Send a GET request to the URL.

    # query and fetch available submission api's
    qs = Provider_meta_data_API.objects.filter(api_meta_type="Submission")
    for api in qs:
        harvester = SubmissionMetadataHarvester(api.base_url)
        last_date = api.last_pull_time.strftime("%Y-%m-%d")
        submissions = harvester.fetch_submissions(last_date)
        if submissions:
            file_type = '.json'
            file_name = str(datetime.datetime.now().strftime("%Y-%m-%d")) + '.json'

            # save the file to temporary location
            with open(file_name, 'w') as f:
                json.dump(submissions, f)
            fs = open(file_name)
            file_size = os.path.getsize(file_name)

            # save the file in table
            try:
                x = Archive.objects.create(
                    file_name_on_source = file_name,
                    provider = api.provider,
                    processed_on = datetime.datetime.now(tz=pytz.utc),
                    status = 'success',
                    file_size = file_size,
                    file_type = file_type
                )

                # save file
                file_name = str(x.id) + '.' + file_name.split('.')[-1]
                x.file_content.save(file_name, fs)

                # close the opened file
                fs.close()

                # remove the file from temp location
                os.remove(file_name)

                # update status
                api.last_pull_time = datetime.datetime.now(tz=pytz.utc)
                api.last_pull_status = 'success'
                api.next_due_date = datetime.datetime.now(tz=pytz.utc) + datetime.timedelta(api.minimum_delivery_fq)
                api.save()

            except Exception as e:
                # if error occured update the failed status
                api.last_pull_time = datetime.datetime.now(tz=pytz.utc)
                api.last_pull_status = 'failed'
                api.last_error_message = e
                api.save()


        else:
            api.last_pull_time = datetime.datetime.now(tz=pytz.utc)
            api.last_pull_status = 'failed'
            api.last_error_message = 'No record found'
            api.save()

    try:
        # zip the file
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        path = os.path.join(settings.SUBMISSION_ROOT , current_date + '.zip')
        # zip_folder(settings.SUBMISSION_ROOT, path)
    except Exception as e:
        print(e)

    return Response("done")



