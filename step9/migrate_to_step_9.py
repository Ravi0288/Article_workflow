from django.shortcuts import render
from rest_framework.decorators import api_view
from model.article import Article
from django.contrib.auth.decorators import login_required
import pickle
from citation import *
from django.conf import settings
from citation_to_marc import citation_to_marc
import os
from model.provider import Providers


@login_required
@api_view(['GET'])
def migrate_to_step9(request):

    # Create MARC_XML_ARTICLE directory if not created already
    if not os.path.exists(settings.MARC_XML_ROOT):
        os.makedirs(settings.MARC_XML_ROOT)

    providers = Providers.objects.filter(in_production=True)
    for provider in providers:
        base = '/ai/metadata/ARTICLE_MARC_XML/' + provider.working_name
        if not os.path.exists(base):
            os.makedirs(base)


    # Set Response message
    context = {
        'heading' : 'Message',
        'message' : 'No pending article found to migrate to Step 9'
    }

    # Fetch all files that need to be processed from Article table
    articles = Article.objects.filter(
        last_status='active',
        provider__in_production=True,
        last_step=8
        # article_switch = True
        )

    if not articles.count() :
        return render(request, 'common/dashboard.html', context=context)
    
    for article in articles:
        article.last_step = 9

        try:
            with open(article.citation_pickle.path, 'rb') as file:
                cit = pickle.load(file)
        except Exception as e:
            print("Error loading pickle file", e)
            article.note += f"9- {e}; "
            article.last_status = 'review'
            article.save()
            continue

        # action for stepp 9
        format = 'xml'
        file_path = (article.article_file.path).replace('ARTICLES', 'ARTICLE_MARC_XML')
        extension = file_path.split('.')[-1]
        file_path = file_path.replace(extension, 'xml')
        message = citation_to_marc(cit, format, file_path)

        # # Save article status and updated citation object
        # with open(article.citation_pickle.path, 'wb') as file:
        #     pickle.dump(cit, file, protocol=pickle.HIGHEST_PROTOCOL)

        # Based on returned message, update the last_status
        if message == 'Successful':
            article.last_status = 'active'
        else:
            article.last_status = 'review'
            article.note += f"9- {message}; "


        article.save()


    # return the response 
    context = {
            'heading' : 'Message',
            'message' : f'''
                All Pending articles successfully migrated to Step 9.
                '''
        } 

    return render(request, 'common/dashboard.html', context=context)