from django.shortcuts import render
from rest_framework.decorators import api_view
from model.article import Article
from django.contrib.auth.decorators import login_required
from citation import *
import metadata_quality_review
import pickle
from model.journal import Journal


def make_override_string(article):
    j = ''
    p = article.provider.requirement_override or ""
    if article.journal:
        j = Journal.objects.get(id=article.journal.id).requirement_override or ""
    # j = article.journal.requirement_override or ""
    return f"{p} | {j}" if p and j else p + ' ' + j



@login_required
@api_view(['GET'])
def migrate_to_step6(request):
    context = {
        'heading' : 'Message',
        'message' : 'No active article found to migrate to Step 6'
    }

    # Fetch all files that need to be processed from Article table
    articles = Article.objects.filter(
        last_status='active',
        provider__in_production=True,
        last_step=5,
        provider__article_switch=True
        )

    if not articles.count() :
        return render(request, 'common/dashboard.html', context=context)
    
    for article in articles:
        article.last_step = 6

        override_string = make_override_string(article)

        try:
            with open(article.citation_pickle.path, 'rb') as file:
                cit = pickle.load(file)
        except Exception as e:
            if article.note == 'none':
                article.note = f"6- {e}; "
            else:
                article.note += f"6- {e}; "

        
            article.last_status = 'review'
            article.save()
            continue

        cit, message = metadata_quality_review.metadata_quality_review(cit, override_string)

        if message == 'dropped':
            article.last_status = 'dropped'

        if not article.type_of_record == "journal-article":
            article.type_of_record = cit.type_of_record

        if cit.local.cataloger_notes:
            if article.note == 'none':
                article.note = f"6- {cit.local.cataloger_notes}; "
            else:
                article.note += f"6- {cit.local.cataloger_notes}; "
            

        article.save()

        # Save the updated pickle content back to the file
        with open(article.citation_pickle.path, 'wb') as file:
            pickle.dump(cit, file, protocol=pickle.HIGHEST_PROTOCOL)


    # return the response
    context = {
            'heading' : 'Message',
            'message' : f'''
                All active articles successfully migrated to Step 6.
                '''
        } 

    return render(request, 'common/dashboard.html', context=context)