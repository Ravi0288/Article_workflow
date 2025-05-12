from django.shortcuts import render
from rest_framework.decorators import api_view
from model.article import Article
from django.contrib.auth.decorators import login_required
from citation import *
import pickle
from model.journal import Journal
import datetime
import re
import pytz


@login_required
@api_view(['GET'])
def migrate_to_step4(request):
    context = {
        'heading' : 'Message',
        'message' : 'No pending article found to migrate to Step 4'
    }

    # Fetch all files that need to be processed from Article table
    articles = Article.objects.filter(
        last_status='active',
        provider__in_production=True,
        last_step=3
        # article_switch = True
        ).exclude(citation_pickle='N/A')

    # if no article found, return response
    if not articles.count() :
        return render(request, 'common/dashboard.html', context=context)

    # iterate articles
    for article in articles:
        article.last_step = 4
        article.note = 'success'

        try:
            with open(article.citation_pickle.path, 'rb') as file:
                cit = pickle.load(file)
        except Exception as e:
            print("Error loading pickle file", e)
            article.last_status = 'review'
            article.note = e
            article.save()
            continue

        citation_journal_dictionary = cit.get_journal_info()
        
        issn_list = list(set(citation_journal_dictionary.get('issn', None)))

        # Check to ensure issns are valid
        issn_regex = r"^[0-9]{4}-[0-9]{3}[0-9xX]$"
        for issn in issn_list:
            if not re.match(issn_regex, issn):
                print(f"Invalid ISSN: {issn} from article with id {article.id}")
                issn_list.remove(issn)

        if len(issn_list) == 0:
            if cit.local.USDA == "yes":
                article.note = "No valid ISSN found"
            else:
                article.last_status = 'review'
                article.note = "No valid ISSN found"
            article.save()
            continue

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
            # If no ISSN match, create new journal entries for each listed issn
            for issn_value in issn_list:
                # Create new journal model
                obj = Journal()
                obj.journal_title = citation_journal_dictionary.get('journal_title', None)
                obj.publisher = citation_journal_dictionary.get('publisher', None)
                obj.issn = issn_value
                obj.doi = citation_journal_dictionary.get("container_DOI", None)
                is_usda_funded = citation_journal_dictionary['usda']

                if is_usda_funded == 'yes':
                    obj.collection_status = 'from_submission'
                else:
                    obj.collection_status = 'pending'
                obj.save()


            article.last_status = "review"
            article.note = "Journal is pending"
            
            if issn_list:
                qs = Journal.objects.filter(issn=issn_list[0])
                if qs.exists():
                    article.journal = qs[0]

        else:
            journal_match = Journal.objects.filter(issn=issn_match).first()
            article.journal = journal_match
            if journal_match.collection_status == 'rejected' and citation_journal_dictionary.get('usda', None) == "no":
                # Reject article as out of scope
                article.last_status = "dropped"
                article.note = "out of scope"
                article.current_date = datetime.datetime.now(tz=pytz.utc)
                article.journal = journal_match
                article.save()
                continue
            else:
                cit.container_DOI = journal_match.doi
                cit.local.identifiers["journal_mmsid"] = journal_match.mmsid
                nal_journal_id = journal_match.nal_journal_id
                cit.local.identifiers["nal_journal_id"] = nal_journal_id
                if journal_match.collection_status == "pending":
                    article.last_status = "review"
                    article.note = "Journal is pending"
                    if citation_journal_dictionary.get("usda", None) == "no":
                        cit.local.cataloger_notes.append('Journal is pending')

        # update the journal id in article
        article.save()

        # Save the updated pickle content back to the file
        with open(article.citation_pickle.path, 'wb') as file:
            pickle.dump(cit, file, protocol=pickle.HIGHEST_PROTOCOL)
        

    # return the response
    context = {
            'heading' : 'Message',
            'message' : f'''
                All Pending articles successfully migrated to Step 4.
                '''
        } 

    return render(request, 'common/dashboard.html', context=context)

