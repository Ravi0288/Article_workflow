from django.shortcuts import render
from rest_framework.decorators import api_view
from model.article import Article
from django.contrib.auth.decorators import login_required
from citation import *
import os
import shutil
from .s3_interaction import AlmaS3Uploader
from model.processsing_state import ProcessingState
from django.conf import settings
import zipfile
import datetime
from django.utils import timezone
from .fetch_s3_secrets import get_aws_credentials


def del_contents(path):
    for entry in os.listdir(path):
        entry_path = os.path.join(path, entry)
        if os.path.isfile(entry_path) or os.path.islink(entry_path):
            os.unlink(entry_path)
        elif os.path.isdir(entry_path):
            shutil.rmtree(entry_path)
    return True

# function to zip and delete the provided directory contents
def zip_and_remove_directory(source_dir: str, output_zip_path: str) -> bool:
    # create backup directory if not created
    os.makedirs(output_zip_path, exist_ok=True)
    output_zip_path = os.path.join(output_zip_path, str(datetime.date.today()).replace('-','_') + '.zip')
    try:
        # Create zip file and add all files/folders recursively
        with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    abs_file_path = os.path.join(root, file)
                    # Add file to zip with relative path
                    rel_path = os.path.relpath(abs_file_path, start=source_dir)
                    zipf.write(abs_file_path, arcname=rel_path)

        # Remove the source directory and all contents
        dir_list = ['MERGE_USDA', 'NEW_USDA', 'MERGE_PUBLISHER', 'NEW_PUBLISHER']
        for item in dir_list:
            del_contents(os.path.join(source_dir, item))
            
        return True, 'successsful'
    except Exception as e:
        return False, e


# update last step of the articles in step 10
def update_step():
    articles = Article.objects.filter(
        last_status='active',
        provider__in_production=True,
        last_step=10,
        provider__article_switch=True
        )
    articles.update(last_step=11)

    # USDA article only should go to next step
    articles.exclude(journal__collection_status = 'from_submission')
    articles.last_status = 'completed'
    # articles.end_date = datetime.datetime.now()
    articles.end_date = timezone.now()
    articles.save()
    return True




def empty_s3(s3_action, context, message):
    empty, reason = s3_action.empty_s3_bucket()
    if empty:
        context['message'] = f'''Error occured while uploading files. Message: {message}. 
            S3 bucket is empty now. All upload files on S3 is removed and the bucket is empty now. 
            Please note the error message for debug purpose.'''
    else:
        context['message'] = f'''Error occured while uploading files. Message: {message}.            
        Also, While trying to empty the uploaded files to S3, another error occurred. Message: {reason}.          
        Please ensure to empty the bucket before running step 11 again.
        Please note the error message for debug purpose.
        '''


@login_required
@api_view(['GET'])
def migrate_to_step11(request):

    step10_state = ProcessingState.objects.filter(process_name='step10')[0]

    context = {
        'heading' : 'Message',
        'message' : 'No active article found to migrate to Step 11'
    }

    # if step 10 is running, return response and ask client to wait till step 10 is running
    if step10_state.in_progress:
        context['message'] = 'Step 10 is running. Please try after sometime. Step 11 can\'t be run till step 10 is running'
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

    stagin_info = {
        'base_s3_uri' : settings.BASE_S3_URI,
        's3_uris' : settings.S3_URIS,
        'aws_access_key' : settings.AWS_S3_ACCESS_KEY,
        'aws_secret_key' : settings.AWS_S3_SECRET_KEY,
        'bucket' : settings.S3_BUCKET,
        'prefix' : settings.S3_PREFIX,
        'base_path' : os.path.join(settings.BASE_DIR, settings.ALMA_STAGING)
    }


    s3_action = AlmaS3Uploader(stagin_info)

    if s3_action.check_s3_buckets_empty():

        # create directories
        created, message = s3_action.create_s3_directories()
        if created:
            uploaded, message = s3_action.upload_directory_to_s3()
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
                    context['message'] = f'''
                        Successfully uploaded all the files, 
                        ALMA_STAGING directory zipped and moved to ALMA_STAGING_backup folder as zip file. 
                        Message : {message}
                    '''
                    # update article last_step
                    update_step()
                    # delete entry of step 10
                    step10_state.delete()

                else:
                    empty_s3(s3_action, context, message)
                
            else:
                empty_s3(s3_action, context, message)
        else:
            context['message'] = f'''Error occurred while creating directories on S3. Please try after sometime.
              Message: {message}''' 
    else:
        context['message'] = 'S3 Bucket is not empty. To continue, please empty the S3 Bucket or contact concern team.'

    
    return render(request, 'common/dashboard.html', context=context)
