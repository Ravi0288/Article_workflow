from django.shortcuts import render
from rest_framework.decorators import api_view
from model.article import Article
from django.contrib.auth.decorators import login_required
from citation import *
import pickle
from type_and_match import type_and_match

@login_required
@api_view(['GET'])
def migrate_to_step5(request):
    context = {
        'heading' : 'Message',
        'message' : 'No pending article found to migrate to Step 5'
    }

    # Fetch all files that need to be processed from Article table
    articles = Article.objects.filter(
        last_status__in=('active', 'dropped'),
        provider__in_production=True,
        last_step=4
        # article_switch = True
        )
    
    print(articles.count(), "######################################")

    if not articles.count() :
        return render(request, 'common/dashboard.html', context=context)
    
    doi_exists = 0
    doi_na = 0
    
    for article in articles:
        # Before unpickling the Citation object, check if the incoming article has a DOI attribute.
        if article.DOI:
            doi_exists=doi_exists + 1
            # If the Article object has a DOI attribute, search for existing article models that have the same DOI, status of "active", and a last_stage greater than 4.
            # If an article is found, skip (ignore) the article and go to the incoming article. The article will be processed after the matching article has been processed and is no longer active in the workflow.
            # If no article is found, continue with loading the Article's Citation object.
            pass
        
        else:
            doi_na=doi_na+1
        # If the Article object does not have a DOI attribute, continue with loading the Article's Citation object.
            try:
                with open(article.citation_pickle.path, 'rb') as file:
                    cit = pickle.load(file)
            except Exception as e:
                print("Error loading pickle file", e)
                continue

            message = None

            # cit = type_and_match.type_and_match.ArticleTyperMatcher(cit)
            
            cit, message= type_and_match.ArticleTyperMatcher.type_and_match(cit)


            # try:

            #     cit, message= type_and_match.type_and_match.ArticleTyperMatcher.type_and_match(cit)
            # except Exception as e:
            #     print(e)
            #     continue

            if message == "dropped":
                article.last_status = "dropped"

            if cit.local.cataloger_notes:
                article.note = cit.local.cataloger_notes
            
            if not article.type_of_record == "journal-article":
                article.type_of_record = cit.type_of_record

            if cit.local.identifiers["mmsid"]:
                article.MMSID = cit.local.identifiers["mmsid"]

            if cit.local.identifiers["pid"]:
                article.PID = cit.local.identifiers["pid"]

            article.last_step = 5
            article.save()

            # Save the updated pickle content back to the file
            with open(article.citation_pickle.path, 'wb') as file:
                pickle.dump(cit, file, protocol=pickle.HIGHEST_PROTOCOL)


    msg = '''DOI exists in {0} records, while no DOI found in {1} records'''.format(doi_exists, doi_na)
    print(msg)
    # return the response
    context = {
            'heading' : 'Message',
            'message' : f'''
                All Pending articles successfully migrated to Step 5.
                '''
        } 

    return render(request, 'common/dashboard.html', context=context)