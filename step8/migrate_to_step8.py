
from django.shortcuts import render
import pid_minter
from rest_framework.decorators import api_view
from model.article import Article
from django.contrib.auth.decorators import login_required
import pickle
from citation import *


@login_required
@api_view(['GET'])
def migrate_to_step8(request):

    context = {
        'heading' : 'Message',
        'message' : 'No pending article found to migrate to Step 8'
    }

    # Fetch all files that need to be processed from Article table
    articles = Article.objects.filter(
        last_status='active',
        provider__in_production=True,
        last_step=7
        # article_switch = True
        ).exclude(journal=None)

    for article in articles:
        article.last_step=8

    Article.objects.bulk_update(articles, ['last_step'])
    # return the response 
    context = {
            'heading' : 'Message',
            'message' : f'''
                All Pending articles successfully migrated to Step 8.
                '''
        } 

    return render(request, 'common/dashboard.html', context=context)