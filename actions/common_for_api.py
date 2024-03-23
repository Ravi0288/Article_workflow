# function to save data in database
import datetime

import pytz
from actions.archive_article import Archived_article_attribute
from django.core.files.base import ContentFile

def save_in_db(api, file_name, file_size, file_type, response):
    # Open a local file with write-binary mode and write the content of the response to it
    qs = Archived_article_attribute.objects.filter(file_name_on_source=file_name) 

    try:
    # if file not available, create new record
        if not(qs.exists()):
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

        # if file exists in db but the size is mismatched, update the record with updated file
        if (qs.exists() and not(qs[0].file_size == file_size)):
            qs[0].processed_on = datetime.datetime.now(tz=pytz.utc),
            qs[0].status = 'success',
            qs[0].file_size = file_size,
            qs[0].file_content.save(file_name, ContentFile(response.content))

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