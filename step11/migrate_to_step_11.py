from django.shortcuts import render
from rest_framework.decorators import api_view
from model.article import Article, Uploaded_article_counter
from django.contrib.auth.decorators import login_required
from citation import *
import os
import shutil
from .upload_to_alma_s3 import AlmaS3Uploader
from model.processsing_state import ProcessingState
from django.conf import settings
import zipfile
import datetime
from django.utils import timezone
from .fetch_s3_secrets import get_aws_credentials
from reports.email import send_email_notification


dir_list = ['MERGE_USDA', 'NEW_USDA', 'MERGE_PUBLISHER', 'NEW_PUBLISHER']

# Function to count and return number of records in each directory
def count_direcotries(path):
    subdirs = [
        name for name in os.listdir(path)
        if os.path.isdir(os.path.join(path, name))
    ]
    return len(subdirs)


# Function to delete content of the provided path 
def del_contents():
    for item in dir_list:
        path =  os.path.join(settings.ALMA_STAGING, item)
        for entry in os.listdir(path):
            entry_path = os.path.join(path, entry)
            if os.path.isfile(entry_path) or os.path.islink(entry_path):
                os.unlink(entry_path)
            elif os.path.isdir(entry_path):
                shutil.rmtree(entry_path)
    return True


# Function to generate a unique filename by appending _1, _2, and so on.
def get_unique_filename(base_path):
    if not os.path.exists(base_path):
        return base_path
    base, ext = os.path.splitext(base_path)
    counter = 1
    new_path = f"{base}_{counter}{ext}"
    while os.path.exists(new_path):
        counter += 1
        new_path = f"{base}_{counter}{ext}"
    return new_path


# Function to zip and delete the provided directory contents
def zip_and_remove_directory(source_dir: str, output_zip_path: str) -> bool:
    # create backup directory if not created
    os.makedirs(output_zip_path, exist_ok=True)

    res = []
    for item in dir_list:
        # prepare data for Uploaded_article_counter
        data_counter = Uploaded_article_counter()
        data_counter.article_count = count_direcotries(os.path.join(source_dir, item))
        data_counter.stage = item

        dir_to_zip = os.path.join(source_dir, item)
        if not os.path.exists(dir_to_zip):
            continue

        # initial zip filename
        base_zip_name = os.path.join(
            output_zip_path, f"{item}_{datetime.date.today().strftime('%Y_%m_%d')}.zip"
        )
        zipped_file = get_unique_filename(base_zip_name)
        data_counter.stage_archive = zipped_file

        try:
            is_empty = True
            # Create zip file and add all files/folders recursively
            with zipfile.ZipFile(zipped_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(os.path.join(source_dir, item)):
                    for file in files:
                        abs_file_path = os.path.join(root, file)
                        # Add file to zip with relative path
                        rel_path = os.path.relpath(abs_file_path, start=source_dir)
                        zipf.write(abs_file_path, arcname=rel_path)
                        is_empty = False

            # if no content available in zipped file, remove it
            if is_empty:
                os.remove(zipped_file)
            
            data_counter.notes = 'Successful'
            res.append(data_counter)
        except Exception as e:
            print("####### Error occured ################### ", e)
            return False, e
     
    Uploaded_article_counter.objects.bulk_create(res)
    return True, 'successsful'


# Update last step of the articles in step 10
def update_step():
    # Get articles to promote from step 10 to 11
    articles = Article.objects.filter(
        last_status='active',
        provider__in_production=True,
        last_step=10,
        provider__article_switch=True
    )
    
    # Update step and end_date
    articles.update(last_step=11, end_date=timezone.now())

    # Update 'completed' status of articles other than usda
    articles = Article.objects.filter(
        last_step=11
    ).exclude(import_type__endswith='usda')
    articles.update(last_status='completed', end_date=timezone.now())
    

    return True




# Function to clear contents of the S3 Bucket
def empty_s3(s3_action, context, message):
    empty, reason = s3_action.empty_s3_bucket()
    if empty:
        context['message'] = f'''Error occured while uploading files. 
            All upload files on S3 is removed and the bucket is empty now. 
            Please note the error message for debug purpose.
            Message: {message}'''
    else:
        context['message'] = f'''Error occured while uploading files.            
        Also, While trying to empty the uploaded files to S3, another error occurred. Message: {reason}.          
        Please ensure to empty the bucket before running step 11 again.
        Please note the error message for debug purpose.
        Message: {message}
        '''


@login_required
@api_view(['GET'])
def migrate_to_step11(request):
   
    context = {
        'heading' : 'Message',
        'message' : 'No active article found to migrate to Step 11'
    }

    # If step 10 is running, return response and ask client to wait till step 10 is running
    step10_state = ProcessingState.objects.filter(process_name='step10') 
    if step10_state.exists():
        state = step10_state[0]
        if state.in_progress:
            context['message'] = (
                "Step 10 is currently running. Please try again later. "
                "Step 11 cannot be executed until Step 10 is complete."
            )
            return render(request, 'common/dashboard.html', context=context)

        # Validation rules
        validation_rules = [
            (state.new_usda_record_processed, settings.NEW_USDA_MIN_LIMIT, "new_usda"),
            (state.merge_usda_record_processed, settings.MERGE_USDA_MIN_LIMIT, "merge_usda"),
            (state.new_publisher_record_processed, settings.NEW_PUBLISHER_MIN_LIMIT, "new_publisher"),
            (state.merge_publisher_record_processed, settings.MERGE_PUBLISHER_MIN_LIMIT, "merge_publisher"),
        ]

        for processed, min_limit, directory in validation_rules:
            if min_limit:
                if processed < min_limit:
                    context['message'] = (
                        f"The number of articles ready for upload, '{processed}', for '{directory}'"
                        f" is below the minimum required threshold of '{min_limit}' articles."
                    )
                    return render(request, 'common/dashboard.html', context=context)

    # Fetch all files that need to be processed from Article table
    articles = Article.objects.filter(
        last_status='active',
        provider__in_production=True,
        last_step=10,
        provider__article_switch=True
        )

    if not articles.count() :
        return render(request, 'common/dashboard.html', context=context)

    # get_aws_credentials function will return key1 and key2 if sucess, else False and error message.
    key1, key2 = get_aws_credentials()
    if not key1:
        context['message'] = key2
        return render(request, 'common/dashboard.html', context=context)        
    
    
    stagin_info = {
        'base_s3_uri' : settings.BASE_S3_URI,
        's3_uris' : settings.S3_URIS,
        'aws_access_key' : key1,
        'aws_secret_key' : key2,
        'bucket' : settings.S3_BUCKET,
        'prefix' : settings.S3_PREFIX,
        'base_path' : os.path.join(settings.BASE_DIR, settings.ALMA_STAGING)
    }


    s3_action = AlmaS3Uploader(stagin_info)

    if s3_action.check_s3_buckets_empty():

        # create directories
        created, message = s3_action.create_s3_directories()
        if created:
            try:
                uploaded, message = s3_action.upload_directory_to_alma_s3()
                if uploaded:
                    # zip the alma_staging directory and save in alma_staging_backup directory as today_date.zip and delete the unzipped files
                    res, message = zip_and_remove_directory(
                        os.path.join(settings.BASE_DIR, settings.ALMA_STAGING),
                        os.path.join(
                            settings.BASE_DIR,
                            settings.ALMA_STAGING_BACKUP
                            )
                        )
                    
                    if res:
                        # Update article last_step
                        update_step()

                        # Delete entry of step 10
                        step10_state.delete()

                        # Delete Alma_staging direcotry
                        del_contents()

                        # Once process run successfully, send email to concern
                        send_email_notification()

                        # Set the success message
                        context['message'] = f'''
                            Successfully uploaded all the files, 
                            ALMA_STAGING directory zipped and moved to ALMA_STAGING_backup folder as zip file. 
                            Message : {message}
                        '''

                    else:
                        empty_s3(s3_action, context, message)
                    
                else:
                    empty_s3(s3_action, context, message)

            except Exception as e:
                context['message'] = f'''Error occurred. Message: {e}'''
                empty_s3(s3_action, context, message)

        else:
            context['message'] = f'''Error occurred while creating directories on S3. Please try after sometime.
              Message: {message}''' 
    else:
        context['message'] = 'No AWS buckets are free to receive article stages for import into Alma'

    
    return render(request, 'common/dashboard.html', context=context)
