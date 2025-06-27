
from django.shortcuts import render
import pid_minter
from rest_framework.decorators import api_view
from model.article import Article
from django.contrib.auth.decorators import login_required
import pickle
from citation import *
from annotate_subject_terms import annotate_citation


@login_required
@api_view(['GET'])
def migrate_to_step8(request):

    context = {
        'heading' : 'Message',
        'message' : 'No active article found to migrate to Step 8'
    }

    # Fetch all files that need to be processed from Article table
    articles = Article.objects.filter(
        last_status='active',
        provider__in_production=True,
        last_step=7,
        provider__article_switch=True
        )

    for article in articles:

        # Unpickle citation object
        try:
            with open(article.citation_pickle.path, 'rb') as file:
                cit = pickle.load(file)
        except Exception as e:

            if article.note == 'none':
                article.note = f"8- {e};"
            else:
                article.note += f"8- {e}; "


            article.last_status = 'review'
            article.save()
            continue
        
        subject_cluster = None
        if article.journal:
            subject_cluster = article.journal.subject_cluster

        # apply annotate_with_cogito(citation_object, subject_cluster)
        citation_object, message = annotate_citation(cit, subject_cluster)
        if message == "network error":
            # halt processing
            context = {
                'heading': 'Message',
                'message': f'''
                                        Network error encountered. Try again later.
                                        '''
            }

            return render(request, 'common/dashboard.html', context=context)
        if message == "review":
            article.last_step = 8
            article.last_status = 'review'
            if article.note == "none":
                article.note = "8- insufficient annotations; "
            else:
                article.note += "8- insufficient annotations; "
            article.save()
        elif message == "successful":
            article.last_step = 8
            article.save()
        elif message == "successful, no annotations":
            article.last_step = 8
            if article.note == "none":
                article.note = "8- insufficient annotations; "
            else:
                article.note += "8- insufficient annotations; "
            article.save()
        # Save citation object
        with open(article.citation_pickle.path, 'wb') as file:
            pickle.dump(citation_object, file, protocol=pickle.HIGHEST_PROTOCOL)
    context = {
            'heading' : 'Message',
            'message' : f'''
                All active articles successfully migrated to Step 8.
                '''
        } 

    return render(request, 'common/dashboard.html', context=context)
