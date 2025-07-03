from django.shortcuts import render
from rest_framework.decorators import api_view
from model.article import Article
from django.contrib.auth.decorators import login_required
import pickle
from citation import *
from handle_minter.mint_and_notify import mint_and_notify

@login_required
@api_view(['GET'])
def migrate_to_step12(request):

    context = {
        'heading' : 'Message',
        'message' : 'No active article found to migrate to Step 12'
    }

    # Fetch all files that need to be processed from Article table
    articles = Article.objects.filter(
        last_status='active',
        provider__in_production=True,
        last_step=11,
        provider__article_switch=True
    )

    if len(articles) == 0:
        return render(request, 'common/dashboard.html', context=context)

    for article in articles:

        # Unpickle citation object
        try:
            with open(article.citation_pickle.path, 'rb') as file:
                cit = pickle.load(file)
        except Exception as e:

            if article.note == 'none':
                article.note = f"12- {e};"
            else:
                article.note += f"12- {e}; "

            article.last_status = 'review'
            article.last_step = 12
            article.save()
            continue

        # Create handle_data dict
        handle_data = {
            'pid': article.PID,
            'mmsid': article.MMSID,
            'provider_rec': article.provider_rec.split("submit:")[-1],
            'title': article.title,
            'submitter_email': cit.local.submitter_email,
            'submitter_name': cit.local.submitter_name,
        }

        if handle_data['pid'] is None or handle_data['provider_rec'] is None or \
                handle_data['title'] is None or handle_data['submitter_email'] is None:
            article.last_status = 'review'
            article.last_step = 12
            if article.note == 'none':
                article.note = f"12- Missing required fields in handle_data; "
            else:
                article.note += f"12- Missing required fields in handle_data; "
            article.save()
            continue

        try:
            result, message = mint_and_notify(handle_data)
        except Exception as e:
            if article.note == 'none':
                article.note = f"12- {e}; "
            else:
                article.note += f"12- {e}; "
            article.last_status = 'review'
            article.last_step = 12
            article.save()
            continue

        if result == "not found in Alma":
            pass
        elif result == "review":
            article.last_status = 'review'
            article.last_step = 12
            if article.note == 'none':
                article.note = f"12- {message}; "
            else:
                article.note += f"12- {message}; "
            article.save()
        elif result == "success":
            article.last_step = 12
            article.last_status = 'completed'
            if message != 'success':
                if article.note == 'none':
                    article.note = f"12- {message}; "
                else:
                    article.note += f"12- {message}; "
            article.save()
    context = {
        'heading': 'Message',
        'message': f'''
                    All active articles successfully migrated to Step 12.
                    '''
    }
    return render(request, 'common/dashboard.html', context=context)