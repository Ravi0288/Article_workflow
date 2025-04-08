from django.shortcuts import render
from rest_framework.decorators import api_view
from model.article import Article
from django.contrib.auth.decorators import login_required
from citation import *

@login_required
@api_view(['GET'])
def migrate_to_step6(request):
    context = {
        'heading' : 'Message',
        'message' : 'No pending article found to migrate to Step 6'
    }

    # Fetch all files that need to be processed from Article table
    articles = Article.objects.filter(
        last_status__in=('active', 'dropped'),
        provider__in_production=True,
        last_step=5
        # article_switch = True
        )

    if not articles.count() :
        return render(request, 'common/dashboard.html', context=context)
    
    for item in articles:
        pass


    # return the response
    context = {
            'heading' : 'Message',
            'message' : f'''
                All Pending articles successfully migrated to Step 6.
                '''
        } 

    return render(request, 'common/dashboard.html', context=context)