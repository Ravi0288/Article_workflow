from django.shortcuts import render
from rest_framework.decorators import api_view
from model.article import Article
from django.contrib.auth.decorators import login_required
from citation import *
import pickle
from model.journal import Journal
import datetime


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

    print("Number of articles identified for processing: ", len(articles))

    for item in articles:
        try:
            with open(item.citation_pickle.path, 'rb') as file:
                cit = pickle.load(file)
        except Exception as e:
            print("Error loading pickle file", e)
            continue

        print("Type of cit object: ", type(cit))
        citation_journal_dictionary = cit.get_journal_info()
        #print("Article's journal: ", citation_journal_dictionary.get('journal_title', None))
        
        issn_list = citation_journal_dictionary.get('issn', None)

        issn_match = None
        for issn_value in issn_list:
            qs = Journal.objects.filter(issn=issn_value)
            if qs.exists():
                issn_match = issn_value
                break


        # We will update this value if and when we find a match in our journal lookup model
        # If we don't find a match, it will stay as 'None'
        journal_match = None

        if issn_match is None:
            # If no ISSN match, create new journal
            for issn_value in issn_list:
                # Create new journal model
                obj = Journal()
                obj.journal_title = citation_journal_dictionary.get('journal_title', None)
                obj.publisher = citation_journal_dictionary.get('publisher', None)
                obj.issn = issn_value
                obj.doi = citation_journal_dictionary.get("container_DOI", None)
                obj.last_updated = datetime.datetime.now()
                is_usda_funded = citation_journal_dictionary['usda']

                if is_usda_funded == 'yes':
                    obj.collection_status = 'From Submission'
                else:
                    obj.collection_status = 'pending'
                obj.save()

            item.last_status = "review"
            item.journal = Journal.objects.filter(issn=issn_list[0])[0]

        else:
            journal_match = Journal.objects.filter(issn=issn_match).first()
            item.journal = journal_match
            if journal_match.collection_status == 'rejected' and citation_journal_dictionary.get('usda', None) == "no":
                # Reject article as out of scope
                item.last_status = "dropped"
                item.last_step = 4
                item.note = "out of scope"
                item.current_date = datetime.datetime.now()
                item.journal = journal_match
                continue
            else:
                cit.container_DOI = journal_match.doi
                cit.local.identifiers["journal_mmsid"] = journal_match.mmsid
                nal_journal_id = journal_match.nal_journal_id
                cit.local.identifiers["nal_journal_id"] = nal_journal_id
                if journal_match.collection_status == "pending":
                    item.last_status = "review"
                    if citation_journal_dictionary.get("usda", None) == "no":
                        cit.local.cataloger_notes.append('Journal is pending')

        # update the journal id in article
        item.last_step = 4
        item.save()

        # Save the updated pickle content back to the file
        with open(item.citation_pickle.path, 'wb') as file:
            pickle.dump(cit, file)
        

    # return the response
    context = {
            'heading' : 'Message',
            'message' : f'''
                All Pending articles successfully migrated to Step 4.
                '''
        } 

    return render(request, 'common/dashboard.html', context=context)

