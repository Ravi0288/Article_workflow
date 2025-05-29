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
        'message' : 'No pending article found to migrate to Step 11'
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

        staging_folder = 
        folder_type = 
        min_required_files = 
        s3_uris = 
        archive_path = 
        active = 
        bucket_empty_check = 
        aws_access_key = 
        aws_secret_key = 
        base_s3_uri = 