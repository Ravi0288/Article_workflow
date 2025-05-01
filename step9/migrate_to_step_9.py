from django.shortcuts import render
from rest_framework.decorators import api_view
from model.article import Article
from django.contrib.auth.decorators import login_required
import pickle
from citation import *
from django.conf import settings
from citation_to_marc import citation_to_marc

@login_required
@api_view(['GET'])
def migrate_to_step9(request):
    
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
        try:
            with open(article.citation_pickle.path, 'rb') as file:
                cit = pickle.load(file)
        except Exception as e:
            print("Error loading pickle file", e)
            article.note = e
            article.save()
            continue

        # action for stepp 9
        format = 'xml'
        file_path = (article.article_file.path).replace('ARTICLES', 'ARTICLE_MARCXML')
        extension = file_path.split('.')[-1]
        file_path = file_path.replace(extension, 'xml')
        message = citation_to_marc(cit, format, file_path)

        # # Save article status and updated citation object
        # with open(article.citation_pickle.path, 'wb') as file:
        #     pickle.dump(cit, file, protocol=pickle.HIGHEST_PROTOCOL)

        # if message returns successfull save the article in and update step.
        if message == 'Successful':
            article.last_step = 9
            article.note = 'N/A'

        # if message is not successful update the error message
        else:
            article.note = message

        # finally save the article
        article.save()


    # return the response 
    context = {
            'heading' : 'Message',
            'message' : f'''
                All Pending articles successfully migrated to Step 9.
                '''
        } 

    return render(request, 'common/dashboard.html', context=context)