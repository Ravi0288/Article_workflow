from django.shortcuts import render
from rest_framework.decorators import api_view
from model.article import Article
from django.contrib.auth.decorators import login_required
import pickle
from citation import *
from .create_alma_dir import create_alma_folder
from django.conf import settings


@login_required
@api_view(['GET'])
def migrate_to_step10(request):

    context = {
        'heading' : 'Message',
        'message' : 'No pending article found to migrate to Step 10'
    }

    # Fetch all files that need to be processed from Article table
    articles = Article.objects.filter(
        last_status='active',
        provider__in_production=True,
        last_step=9
        # article_switch = True
        )

    if not articles.count() :
        return render(request, 'common/dashboard.html', context=context)
    
    for article in articles:
        article.last_step = 10
        
        try:
            with open(article.citation_pickle.path, 'rb') as file:
                cit = pickle.load(file)
        except Exception as e:
            print("Error loading pickle file", e)
            article.note += f"; 10- {e}"
            article.last_status = 'review'
            article.save()
            continue
        
        base = settings.MEDIA_ROOT

        citation_pickle = article.citation_pickle.path
        article_file = article.article_file.path
        marc_file = article.citation_pickle.path
        manuscript_file = article.article_file.path

        path_directory = {
            'citation_pickle' : citation_pickle,
            'article_file' : article_file,
            'marc_file' : marc_file,
            'manuscript_file' : manuscript_file,
        }

        message, cit = create_alma_folder(cit, base, path_directory)

        # Save article status and updated citation object
        with open(article.citation_pickle.path, 'wb') as file:
            pickle.dump(cit, file, protocol=pickle.HIGHEST_PROTOCOL)

        #  Based on returned message, update the last_status
        if message == 'Successful':
            article.last_status = 'active'
        else:
            article.last_status = 'review'
            article.note += f"; 10- {message}"

        article.save()

    # return the response 
    context = {
            'heading' : 'Message',
            'message' : f'''
                All Pending articles successfully migrated to Step 10.
                '''
        } 

    return render(request, 'common/dashboard.html', context=context)