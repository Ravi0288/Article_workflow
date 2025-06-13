from django.shortcuts import render
from rest_framework.decorators import api_view
from model.article import Article
from django.contrib.auth.decorators import login_required
from citation import *
import pickle
from type_and_match.type_and_match import ArticleTyperMatcher
from .network_check import perform_network_connection_check

@login_required
@api_view(['GET'])
def migrate_to_step5(request):

    context = {
        'heading' : 'Message',
        'message' : 'No active article found to migrate to Step 5'
    }

    # Fetch all files that need to be processed from Article table
    articles = Article.objects.filter(
        last_status='active',
        provider__in_production=True,
        last_step=4,
        provider__article_switch=True
    ) 
    
    # if No active article found, exit the function with msessage
    if not articles.count() :
        return render(request, 'common/dashboard.html', context=context)
    

    # If DOI providers URL returns error, Dont proceed further, exit the function with message
    url_list = perform_network_connection_check()
    if url_list:
        context = {
            'heading' : 'Message',
            'message' : f'''Error occured in URLs: {url_list}'''
        }
        return render(request, 'common/dashboard.html', context=context)

    # iterate through the articles
    for i, article in enumerate(articles):
        if article.DOI and article.DOI != "":
            this_doi = article.DOI
            doi_matching_articles = Article.objects.filter(DOI=this_doi, last_step__gt=4)
            if len(doi_matching_articles) > 0:
                # Leave this record at step 4 with status 'active'. Continue processing when record with matching DOI
                # has completed processing
                #print(f"Record with matching DOI found for article with doi {this_doi}")
                continue
        else:
            # For now, if there is no DOI (ie from a submit site record), send the article to review
            # In a future enhancement we will override this to check for matches by submission node id
            article.last_status = "review"
            article.last_step = 5
            if article.note == 'none':
                article.note = f"5- No DOI;"
            else:
                article.note += f"5- No DOI; "
            article.save()
            continue



        # Read in the citation object
        try:
            with open(article.citation_pickle.path, 'rb') as file:
                cit = pickle.load(file)
        except Exception as e:

            if article.note == 'none':
                article.note = f"5- {e};"
            else:
                article.note += f"5- {e}; "


            article.last_status = 'review'
            article.save()
            continue

        ATM = ArticleTyperMatcher()
        cit, message = ATM.type_and_match(cit)

        if message == "Network error, re-run":
            context = {
                'heading': 'Message',
                'message': f'''
                            Network error encountered. Try again later.
                            '''
            }

            return render(request, 'common/dashboard.html', context=context)

        if message == "dropped":
            if article.note == 'none':
                article.note = f"5- {cit.local.cataloger_notes}; "
            else:
                article.note += f"5- {cit.local.cataloger_notes}; "
            article.last_status = "dropped"
            article.last_step = 5
            article.save()
            # Save the updated pickle content back to the file
            with open(article.citation_pickle.path, 'wb') as file:
                pickle.dump(cit, file, protocol=pickle.HIGHEST_PROTOCOL)
            continue

        if message == "review":
            if article.note == 'none':
                article.note = f"5- {cit.local.cataloger_notes}; "
            else:
                article.note += f"5- {cit.local.cataloger_notes}; "
            article.last_status = "review"
            article.last_step = 5
            article.save()
            # Save the updated pickle content back to the file
            with open(article.citation_pickle.path, 'wb') as file:
                pickle.dump(cit, file, protocol=pickle.HIGHEST_PROTOCOL)
            continue

        is_USDA = cit.local.USDA
        if is_USDA == "yes":
            if message == "new":
                article.import_type = "new_usda"
            elif message == "merge":
                article.import_type = "merge_usda"
        elif is_USDA == "no":
            if message == "new":
                article.import_type = "new_publisher"
            elif message == "merge":
                article.import_type = "merge_publisher"

        if not article.type_of_record == "journal-article":
            article.type_of_record = cit.type_of_record

        if cit.local.identifiers.get("mms_id", None):
            article.MMSID = cit.local.identifiers["mms_id"]

        if cit.local.identifiers.get("pid", None):
            article.PID = cit.local.identifiers["pid"]

        article.last_step = 5
        article.save()

        # Save the updated pickle content back to the file
        with open(article.citation_pickle.path, 'wb') as file:
            pickle.dump(cit, file, protocol=pickle.HIGHEST_PROTOCOL)


    # return the response
    context = {
            'heading' : 'Message',
            'message' : f'''
                All active articles successfully migrated to Step 5.
                '''
        } 

    return render(request, 'common/dashboard.html', context=context)