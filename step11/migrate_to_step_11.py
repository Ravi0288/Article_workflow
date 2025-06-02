from django.shortcuts import render
from rest_framework.decorators import api_view
from model.article import Article
from django.contrib.auth.decorators import login_required
import pickle
from citation import *
from article_staging import create_alma_dir
from django.conf import settings
import os
import shutil
from .s3_interaction import AlmaS3Uploader


@login_required
@api_view(['GET'])
def migrate_to_step11(request):

    context = {
        'heading' : 'Message',
        'message' : 'No active article found to migrate to Step 11'
    }

    # Fetch all files that need to be processed from Article table
    articles = Article.objects.filter(
        last_status='active',
        provider__in_production=True,
        last_step=10,
        provider__article_switch=True
        )

    if not articles.count() :
        return render(request, 'common/dashboard.html', context=context)
    
    for article in articles:
        article.last_step = 11

        staging_folder = None
        folder_type =None
        min_required_files = None
        s3_uris = None
        archive_path = None
        active = None
        bucket_empty_check = None
        aws_access_key = None
        aws_secret_key = None
        base_s3_uri = None
        
        pass