
from django.shortcuts import render
from .mint import pid_minter
from rest_framework.decorators import api_view
from model.article import Article
from django.contrib.auth.decorators import login_required
import pickle
from citation import *

@login_required
@api_view(['GET'])
def migrate_to_step7(request):

    context = {
        'heading' : 'Message',
        'message' : 'No pending article found to migrate to Step 7'
    }

    # Fetch all files that need to be processed from Article table
    articles = Article.objects.filter(
        last_status='active',
        provider__in_production=True,
        last_step=6
        # article_switch = True
        )

    if not articles.count() :
        return render(request, 'common/dashboard.html', context=context)
    
    for article in articles:
        try:
            with open(article.citation_pickle.path, 'rb') as file:
                unpickle_content = pickle.load(file)
        except Exception as e:
            print("Error loading pickle file", e)
            article.note = e
            article.save()
            continue

        unpickle_content, message, pid = pid_minter(unpickle_content)

        # Save the updated pickle content back to the file
        with open(article.citation_pickle.path, 'wb') as file:
            pickle.dump(unpickle_content, file, protocol=pickle.HIGHEST_PROTOCOL)

        # Update the article status and note in the database
        if pid:
            article.PID = pid
            article.last_step = 7
            article.note = 'N/A'
            article.save()


    # return the response 
    context = {
            'heading' : 'Message',
            'message' : f'''
                All Pending articles successfully migrated to Step 7.
                '''
        } 

    return render(request, 'common/dashboard.html', context=context)