from html2text import html2text
import requests
from .common_for_api import save_in_db
from django.http import HttpResponse
import pytz
import datetime
import os



class SubmissionMetadataHarvester:
    def __init__(self, base_url):
        self.base_url = base_url

    def fetch_submissions(self, last_date):
        page = 0
        all_submission = []

        while True:
            url = f"{self.base_url}?page={page}&newer-than={last_date}"
            response = requests.get(url)

            if response.status_code != 200:
                print(f"Failed to fetch submission. Status code : {response.status_code}")
                break
            submissions = response.json()
            if not submissions:
                break
            all_submission.extend(submissions)
            page += 1
        return all_submission
    

# function to handle submission api's
def download_from_submission_api(api):
    # Send a GET request to the URL.
    harvester = SubmissionMetadataHarvester(api.base_url)
    last_date = api.last_pull_time.strftime("%Y-%m-%d")
    submissions = harvester.fetch_submissions(last_date)
    if submissions:
        for submission in submissions:
            content_disposition = submission.get('content-disposition')
            if content_disposition:
        # Retrieve file name and file size from response headers

                file_name = 'submission/' + content_disposition.split('filename=')[1]
                 # Use URL as filename if content-disposition is not provided
            else:
                file_name = 'submission/' + os.path.basename(submission.get('url'))
            file_size = int(submission.get('content-length', 0))

        
        
            file_type = os.path.splitext(file_name)[1]

        save_in_db(api, file_name, file_size, file_type, submission)

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