from html2text import html2text
import requests

from step1.archive_article import Archived_article_attribute
from step1.providers import Provider_meta_data_API
from .common_for_api import save_in_db
from django.http import HttpResponse
import pytz
import datetime
import os
from rest_framework.decorators import api_view
from django.core.files.base import ContentFile
import json
from django.conf import settings


class SubmissionMetadataHarvester:
    def __init__(self, base_url):
        self.base_url = base_url

    def fetch_submissions(self, last_date):
        page = 0
        all_submission = []

        while True:
            url = self.base_url.format(my_page=page, last_date = '2024-02-23')
            response = requests.get(url)

            if response.status_code != 200:
                print(f"Failed to fetch submission. Status code : {response.status_code}")
                break
            if len(response.json()) == 0:
                print("exiting no data found")
                break
            submissions = response.json()
            # if not submissions:
            #     break
            all_submission.extend(submissions)
            page += 1
            print(page)
        return all_submission
    

# function to handle submission api's
@api_view(['GET'])
def download_from_submission_api(request):
    # Send a GET request to the URL.
    qs = Provider_meta_data_API.objects.filter(api_meta_type="Submission")
    for api in qs:
        harvester = SubmissionMetadataHarvester(api.base_url)
        last_date = api.last_pull_time.strftime("%Y-%m-%d")
        submissions = harvester.fetch_submissions(last_date)
        if submissions:
            file_type = '.json'
            # file_name = os.path.join(settings.SUBMISSION_ROOT + str(datetime.datetime.now().strftime("%Y-%m-%d")) + '.json')
            file_size = 0
            file_name = str(datetime.datetime.now().strftime("%Y-%m-%d")) + '.json'

            try:
                x = Archived_article_attribute.objects.create(
                    file_name_on_source = file_name,
                    provider = api.provider,
                    processed_on = datetime.datetime.now(tz=pytz.utc),
                    status = 'success',
                    file_size = file_size,
                    file_type = file_type
                )
                # save file
                with open(file_name, 'w') as f:
                    json.dump(submissions, f)
                fs = open(file_name)
                x.file_content.save(file_name, fs)

                # update status
                api.last_pull_time = datetime.datetime.now(tz=pytz.utc)
                api.last_pull_status = 'success'
                api.next_due_date = datetime.datetime.now(tz=pytz.utc) + datetime.timedelta(api.minimum_delivery_fq)
                api.save()

            except Exception as e:
                api.last_pull_time = datetime.datetime.now(tz=pytz.utc)
                api.last_pull_status = 'failed'
                api.last_error_message = e
                api.save()


        else:
            api.last_pull_time = datetime.datetime.now(tz=pytz.utc)
            api.last_pull_status = 'failed'
            api.last_error_message = 'No submission found within the specified data range'
            api.save()

        return HttpResponse("done")





    # # function to handle submission api's
    # def download_from_submission_api(api):
    #     # Send a GET request to the URL.
    #     response = requests.get((api.base_url).format(my_page=api.page_number, last_date = api.last_pull_time))
    #     print(response.text)
    #     if response.status_code == 200:
    #         # Retrieve file name and file size from response headers

    #         file_name = 'submission/' + str(datetime.datetime.now()) +  '.json' # Use URL as filename if content-disposition is not provided
            
    #         file_size = int(response.headers.get('content-length', 0))
    #         file_type = os.path.splitext(file_name)[1]

    #         save_in_db(api, file_name, file_size, file_type, response)

    #     else:
    #         api.last_pull_time = datetime.datetime.now(tz=pytz.utc)
    #         api.last_pull_status = 'failed'
    #         api.last_error_message = '=>// error code = error-code =' + str(response.status_code) + ' =>// error message = ' + html2text(response.text)
    #         api.save()

    #     return HttpResponse("done")