from mapper import mapper
from rest_framework.decorators import api_view
from model.article import Article
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
# from metadata_routines.citation import Citation
from citation import *


# Function to read xml / json file in utf-8 mode. This function will return file content
def read_and_return_file_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        file_content = f.read()
        f.close()
    return file_content        


# Main function to migrate Step 2 files to Step 3
@login_required
@api_view(['GET'])
def migrate_to_step3(request):

    # Fetch all files that need to be processed from Article table
    articles = Article.objects.filter(
        last_status__in=('active', 'failed'),
        provider__in_production=True, 
        last_step=2,
        # provider__in = (9,10)
        )
    # provider__in = (9,10) Remove this line when working with all the providers.
 
    print(articles.count(), " Article found to be migrated to step 3")

    counter=0

    if not articles.exists():
        context = {
            'heading' : 'Message',
            'message' : 'No pending article found to migrate to Step 3'
        }

    else:
        for item in articles:
            # read and return file content in utf-8 format
            file_content = read_and_return_file_content(item.article_file.path)
            # read and return citation_object
            citation_object, msg_string = mapper(file_content, item.provider.source_schema) 

            # if mapper function returns unsuccessful result, update the status and iterate next article
            if msg_string != 'success':
                print("article id: ", item.id ," Mapper function returned: '",msg_string,"'. Skiping this iteration")
                item.last_status = 'failed'
                item.save()
                continue

            # if mapper function returns successful result than update the article
            try:
                obj = Citation.step3_info(citation_object)
                item.title = obj["title"]
                item.type_of_record = obj["type"]
                item.provider_rec = obj["provider_rec"]
                item.note = 'N/A'
                item.DOI = obj["doi"]
                # Finally update the step2 record status 
                item.last_status = 'active'
                item.last_step = 3 
                item.save()
                print("last status of article is updated. Going to next iteration")
                counter +=1
                
            except Exception as e:
                print(item.article_file.path)
                print(e)
                print("error occured while updating the article. Going to next iteration")
 
        context = {
            'heading' : 'Message',
            'message' : f'''{counter} valid articles from step 2 successfully migrated to Step 3'''
        }

    return render(request, 'common/dashboard.html', context=context)


