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

    # Fetch all files that need to be processed from Article table
    articles = Article.objects.filter(
        last_status__in=('active', 'dropped'),
        provider__in_production=True, 
        last_step=3
        # article_switch = True
        ).exclude(citation_pickle='N/A')

    if not articles.count() :
        return render(request, 'common/dashboard.html', context=context)

    for article in articles:
        try:
            with open(article.citation_pickle.path, 'rb') as file:
                unpickle_content = pickle.load(file)
        except Exception as e:
            print("Error loading pickle file", e)
            article.note = e.message
            article.save()
            continue


        citaton_journal_dictionary = Citation.get_journal_info(unpickle_content)

        unpickle_content = unpickle_content.__dict__
        
        issn_list = citaton_journal_dictionary.get('issn', None)

        # iterate over the recieved list of issn 
        for issn_value in issn_list:
            qs = Journal.objects.filter(issn=issn_value)
            # if no match found against the issn number, create new journal
            if not(qs.exists()):
                obj = Journal()
                obj.journal_title = citaton_journal_dictionary.get('journal_title', None)
                obj.publisher = citaton_journal_dictionary.get('publisher', None)
                obj.issn = issn_value
                is_usda_funded = citaton_journal_dictionary['usda']

                if is_usda_funded == 'yes':
                    obj.collection_status = 'From Submission'
                else:
                    obj.collection_status = 'pending' 
                    
                obj.harvest_source = citaton_journal_dictionary.get('harvest_source', None)
                obj.doi = citaton_journal_dictionary.get('doi', None)
                obj.nal_journal_id = citaton_journal_dictionary.get('nal_journal_id', None)
                obj.mmsid = citaton_journal_dictionary.get('mmsid', None)
                obj.note = citaton_journal_dictionary.get('note', None)
                obj.requirement_override = citaton_journal_dictionary.get('requirement_override', None)
                obj.subject_cluster = citaton_journal_dictionary.get('subject_cluster', None)
                obj.save()

                # update the citation object
                unpickle_content['journal_mmsid'] = obj.mmsid
                unpickle_content['nal_journal_id'] = obj.nal_journal_id

            # if match is found, update the existing journal
            else:
                is_usda_funded = citaton_journal_dictionary['usda']
                if is_usda_funded == 'yes':
                    qs[0].collection_status = 'From Submission'
                else:
                    qs[0].collection_status = 'pending'
                    
                qs[0].nal_journal_id = citaton_journal_dictionary.get('nal_journal_id', None)
                qs[0].mmsid = citaton_journal_dictionary.get('mmsid', None)
                qs[0].doi = citaton_journal_dictionary.get('doi', None)
                qs[0].save()

                unpickle_content['journal_mmsid'] = qs[0].mmsid
                unpickle_content['nal_journal_id'] = qs[0].nal_journal_id


        # update the jounal id in article
        article.journal = citaton_journal_dictionary.get('nal_journal_id', None)
        article.last_step = 4
        article.save() 

        # update the cataloger note in pickle file
        note = ''
        if is_usda_funded == 'no':
            note = 'Journal is pending'
        
        try:
            # try to add the value and assume it is already
            unpickle_content['local']['cataloger_note']['note'] = note
        except TypeError:
            # if local key not present in the unpickle_content, add the key
            unpickle_content['local'] = {}
            unpickle_content['local']['cataloger_note'] = {}
            unpickle_content['local']['cataloger_note']['note'] = note

        # Save the updated pickle content back to the file
        with open(article.citation_pickle.path, 'wb') as file:
            pickle.dump(unpickle_content, file)
        

    # retrn the response 
    context = {
            'heading' : 'Message',
            'message' : f'''
                All Pending articles successfully migrated to Step 4.
                '''
        } 

    return render(request, 'common/dashboard.html', context=context)

