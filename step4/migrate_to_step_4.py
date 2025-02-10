from django.shortcuts import render
from rest_framework.decorators import api_view
from model.article import Article
from django.contrib.auth.decorators import login_required
from citation import *
import pickle
from model.journal import Journal


@login_required
@api_view(['GET'])
def migrate_to_step4(request):
    context = {
        'heading' : 'Message',
        'message' : 'No pending article found to migrate to Step 4'
    }

    created = 0
    updated = 0
    # Fetch all files that need to be processed from Article table
    articles = Article.objects.filter(
        last_status__in=('active', 'dropped'),
        provider__in_production=True, 
        last_step=3,
        # article_switch = True
        )

    print("Total article to ready to be processed in step 4 :", articles.count())

    if not articles.count() :
        return render(request, 'common/dashboard.html', context=context)

    for item in articles:
        with open(item.citation_pickle.path, 'rb') as file:
            pickle_content = pickle.load(file)

        citaton_journal_dictionary = Citation.get_journal_info(pickle_content)
        
        obj = Journal()

        # if journal is not availale for article, create new journal
        if not item.journal:
            obj.journal_title = citaton_journal_dictionary.get('journal_title', None)
            obj.publisher = citaton_journal_dictionary.get('publisher', None)
            obj.issn = citaton_journal_dictionary.get('issn', None)
            obj.collection_status = citaton_journal_dictionary.get('collection_status', None)
            obj.harvest_source = citaton_journal_dictionary.get('harvest_source', None)
            obj.local_id = citaton_journal_dictionary.get('local_id', None)
            obj.mmsid = citaton_journal_dictionary.get('mmsid', None)
            obj.note = citaton_journal_dictionary.get('note', None)
            obj.save()

            item.journal = obj
            item.last_step = 4
            item.save()
            created += 1
        
        # if journal is available, update the journal
        else:
            obj.journal_title = citaton_journal_dictionary.get('journal_title', None)
            obj.publisher = citaton_journal_dictionary.get('publisher', None)
            obj.issn = citaton_journal_dictionary.get('issn', None)
            obj.collection_status = citaton_journal_dictionary.get('collection_status', None)
            obj.harvest_source = citaton_journal_dictionary.get('harvest_source', None)
            obj.local_id = citaton_journal_dictionary.get('local_id', None)
            obj.mmsid = citaton_journal_dictionary.get('mmsid', None)
            obj.note = citaton_journal_dictionary.get('note', None)
            obj.save()

            item.last_step = 4
            item.save()

            updated += 1
        
    context = {
            'heading' : 'Message',
            'message' : f'''
                {0} new journal created and {1} journals updated 
                '''.format(created, updated)
        } 

    return render(request, 'common/dashboard.html', context=context)

