from django.shortcuts import render
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import login_required
from django.conf import settings
import os
from .s3_interaction import AlmaS3Uploader


@login_required
@api_view(['GET'])
def empty_s3_bucket(request):

    stagin_info = {
        'base_s3_uri' : settings.BASE_S3_URI,
        's3_uris' : settings.S3_URIS,
        'aws_access_key' : settings.AWS_S3_ACCESS_KEY,
        'aws_secret_key' : settings.AWS_S3_SECRET_KEY,
        'bucket' : settings.S3_BUCKET,
        'prefix' : settings.S3_PREFIX,
        'base_path' : os.path.join(settings.BASE_DIR, settings.ALMA_STAGING)
    }
        
    context = {
        'heading' : 'Message',
        'message' : f'''S3 Bucket emptied successfully. '''
    }


    s3_action = AlmaS3Uploader(stagin_info)
    empty, message = s3_action.empty_s3_bucket()

    if not empty:
        context['message'] = f''' 
            Error occured while emptying S3. 
            Message: {message}.
        '''

    return render(request, 'common/dashboard.html', context=context)