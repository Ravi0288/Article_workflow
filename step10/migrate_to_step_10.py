from django.shortcuts import render
from rest_framework.decorators import api_view
from model.article import Article, ProcessedArticleHistory
from model.processsing_state import ProcessingState
from django.contrib.auth.decorators import login_required
import pickle
from citation import *
from article_staging import create_alma_dir
from django.conf import settings
import os
import shutil

# Function to accept article file path as input, and just will replace the extension with xml to make it as marc xml file
def get_marc_file_path(article_file_path):
    extension = article_file_path.split('.')[-1]
    return article_file_path.replace(extension, 'xml').replace('ARTICLES','ARTICLE_MARC_XML')


@login_required
@api_view(['GET'])
def migrate_to_step10(request):

    context = {
        'heading' : 'Message',
        'message' : 'No active article found to migrate to Step 10'
    }

    # if step10 is running, don't allow it to run for second time
    step10_state, created = ProcessingState.objects.get_or_create(process_name='step10')
    
    if created:
        if step10_state.in_progress:
            context['message'] = 'Step 10 is already running. Please try after sometime'
            return render(request, 'common/dashboard.html', context=context)
        else:
            step10_state.in_progress = True
            step10_state.save()

            # Initialize counters with existing counter
            counters = {
                "new_usda": step10_state.new_usda_record_processed,
                "merge_usda": step10_state.merge_usda_record_processed,
                "new_publisher": step10_state.new_publisher_record_processed,
                "merge_publisher": step10_state.merge_publisher_record_processed,
            }

    else:
        # Initialize counters
        counters = {
            "new_usda": 0,
            "merge_usda": 0,
            "new_publisher": 0,
            "merge_publisher": 0,
        }

    # Fetch all files that need to be processed from Article table
    articles = Article.objects.filter(
        last_status='active',
        provider__in_production=True,
        last_step=9,
        provider__article_switch=True
        )

    if not articles.count() :
        step10_state.in_progress = False
        step10_state.save()
        return render(request, 'common/dashboard.html', context=context)
    

    VALID_IMPORT_TYPES = {'new_usda', 'merge_usda', 'new_publisher', 'merge_publisher'}

    # Mapping of import types to their corresponding limit settings
    MAX_LIMIT = {
        "new_usda": settings.NEW_USDA_MAX_LIMIT,
        "merge_usda": settings.MERGE_USDA_MAX_LIMIT,
        "new_publisher": settings.NEW_PUBLISHER_MAX_LIMIT,
        "merge_publisher": settings.MERGE_PUBLISHER_MAX_LIMIT,
    }

    for article in articles:
        article.last_step = 10

        # Skip processing this article if its import_type has already reached the maximum allowed limit.
        import_type = article.import_type
        if import_type in counters:
            counters[import_type] += 1
            if counters[import_type] > MAX_LIMIT[import_type]:
                continue

        # Ensure each article has a valid import_type classification.
        if not article.import_type or article.import_type not in VALID_IMPORT_TYPES:
            article.note += f"Bad Import type found: {article.import_type}\n"
            article.last_status = 'review'
            article.save()
            continue

        # Start processing all valid articles
        try:
            with open(article.citation_pickle.path, 'rb') as file:
                cit = pickle.load(file)
        except Exception as e:
            if article.note == 'none':
                article.note = f"10- {e}; "
            else:
                article.note += f"10- {e}; "
            article.last_status = 'review'
            article.save()
            continue
        
        base = settings.MEDIA_ROOT

        citation_pickle = article.citation_pickle.path
        article_file = article.article_file.path
        marc_file = get_marc_file_path(article.article_file.path)
        # manuscript_file = article.article_file.path

        path_directory = {
            'citation_pickle' : citation_pickle,
            'article_file' : article_file,
            'marc_file' : marc_file,
            # 'manuscript_file' : manuscript_file,
        }

        message, cit, article_stage_dir = create_alma_dir.create_alma_directory(cit, base, path_directory, article)

        # Save updated citation object file
        with open(article.citation_pickle.path, 'wb') as file:
            pickle.dump(cit, file, protocol=pickle.HIGHEST_PROTOCOL)

        #  Based on returned message, update the last_status
        if message == 'Successful':
            article.last_status = 'active'
        else:
            article.last_status = 'review'

            if article.note == 'none':
                article.note = f"10- {message};"
            else:
                article.note += f"10- {message};"

            # if error occured, delete the entire directory
            if article_stage_dir and os.path.exists(article_stage_dir):
                shutil.rmtree(article_stage_dir)

        article.save()

    # return the response 
    context = {
            'heading' : 'Message',
            'message' : f'''
                All active articles successfully migrated to Step 10.
                '''
        } 
    
    ProcessedArticleHistory.objects.create(
        new_usda_record_processed = counters['new_usda'],
        merge_usda_record_processed = counters['merge_usda'],
        new_publisher_record_processed = counters['new_publisher'],
        merge_publisher_record_processed = counters['merge_publisher'],
    )


    # update step 10 record with number of processed articles based on classification
    step10_state.in_progress = False
    step10_state.new_usda_record_processed = counters["new_usda"]
    step10_state.merge_usda_record_processed = counters["merge_usda"]
    step10_state.new_publisher_record_processed = counters["new_publisher"]
    step10_state.merge_publisher_record_processed = counters["merge_publisher"]
    step10_state.save()

    return render(request, 'common/dashboard.html', context=context)