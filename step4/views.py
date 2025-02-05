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
        last_status__in=('active', 'failed'),
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

        # # citaton_journal_dictionary = Citation.get_journal_info(pickle_content)

        # # if journal is not availale for article, create new journal
        # if not item.journal:
        #     obj = Journal()
        #     obj['journal_title'] = citaton_journal_dictionary['journal_title']
        #     obj['publisher'] = citaton_journal_dictionary['publisher']
        #     obj['issn'] = citaton_journal_dictionary['issn']
        #     obj['collection_status'] = citaton_journal_dictionary['collection_status']
        #     obj['harvest_source'] = citaton_journal_dictionary['harvest_source']
        #     obj['local_id'] = citaton_journal_dictionary['local_id']
        #     obj['mmsid'] = citaton_journal_dictionary['mmsid']
        #     obj['note'] = citaton_journal_dictionary['note']
        #     obj.save()

        #     item.journal = obj
        #     created += 1
        
        # # if journal is available, update the journal
        # else:
        #     obj['journal_title'] = citaton_journal_dictionary['journal_title']
        #     obj['publisher'] = citaton_journal_dictionary['publisher']
        #     obj['issn'] = citaton_journal_dictionary['issn']
        #     obj['collection_status'] = citaton_journal_dictionary['collection_status']
        #     obj['harvest_source'] = citaton_journal_dictionary['harvest_source']
        #     obj['local_id'] = citaton_journal_dictionary['local_id']
        #     obj['mmsid'] = citaton_journal_dictionary['mmsid']
        #     obj['note'] = citaton_journal_dictionary['note']
        #     obj.save()

        #     updated += 1
        
    context = {
            'heading' : 'Message',
            'message' : f'''
                {0} valid articles from step 3 to be migrated to Step-4. 
                {1} new journal created and {2} journals updated 
                '''.format(articles.count(), created, updated)
        }

    return render(request, 'common/dashboard.html', context=context)

