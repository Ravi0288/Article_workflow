
from django.shortcuts import render
import pid_minter
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
        'message' : 'No active article found to migrate to Step 7'
    }

    # Fetch all files that need to be processed from Article table
    articles = Article.objects.filter(
        last_status='active',
        provider__in_production=True,
        last_step=6,
        provider__article_switch=True
        )

    if not articles.count() :
        return render(request, 'common/dashboard.html', context=context)
    
    for article in articles:
        article.last_step = 7

        try:
            with open(article.citation_pickle.path, 'rb') as file:
                cit = pickle.load(file)
        except Exception as e:
            if article.note == 'none':
                article.note = f"7- {e}; "
            else:
                article.note += f"7- {e}; "

            article.last_status = 'review'
            article.save()
            continue
            
        # is_usda_funded = (article.journal.collection_status == 'from_submission')
        is_usda_funded = cit.local.USDA
        cit, message, pid = pid_minter.pid_minter(cit, is_usda_funded)

        # Save the updated pickle content back to the file
        with open(article.citation_pickle.path, 'wb') as file:
            pickle.dump(cit, file, protocol=pickle.HIGHEST_PROTOCOL)

        # Update the article status and note in the database
        if pid:
            article.PID = pid

        if cit.local.identifiers.get("mms_id", None):
            article.MMSID = cit.local.identifiers["mms_id"]

        if message != 'PID Assigned':
            if article.note == 'none':
                article.note = f"7- {message}; "
            else:
                article.note += f"7- {message}; "
            
        article.save()


    # return the response 
    context = {
            'heading' : 'Message',
            'message' : f'''
                All active articles successfully migrated to Step 7.
                '''
        } 

    return render(request, 'common/dashboard.html', context=context)