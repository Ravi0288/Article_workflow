from django.shortcuts import render
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import login_required
from django.conf import settings
import os
# from .upload_to_alma_s3 import AlmaS3Uploader
# from .fetch_s3_secrets import get_aws_credentials
from alma_s3 import get_aws_credentials, AlmaS3Uploader

@login_required
@api_view(['GET'])
def empty_s3_bucket(request):

    context = {
        'heading' : 'Message',
        'message' : f'''S3 Bucket emptied successfully. '''
    }

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
    empty, message = s3_action.empty_s3_bucket()

    if not empty:
        context['message'] = f''' 
            Error occured while emptying S3. 
            Message: {message}.
        '''

    return render(request, 'common/dashboard.html', context=context)