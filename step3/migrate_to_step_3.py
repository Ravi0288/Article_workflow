from mapper import mapper
from rest_framework.decorators import api_view
from model.article import Article
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from citation import *
import pickle
from io import BytesIO
from django.core.files import File
from django.core.files.storage import default_storage
import os


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
        last_status__in=('active', 'dropped'),
        provider__in_production=True, 
        last_step=2,
        provider__working_name__in = ('SUBMISSION', 'CHORUS')
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
        for article in articles:
            # read and return file content in utf-8 format
            file_content = read_and_return_file_content(article.article_file.path)
            # read and return citation_object

            try:
                citation_object, msg_string = mapper(file_content, article.provider.source_schema) 
            except Exception as e:
                print("Error Occured from mapper function for article id :", article.id, "error Message :", e)
                continue

            # if mapper function returns unsuccessful result, update the status and iterate next article
            if msg_string != 'success':
                print("article id: ", article.id ," Mapper function returned: ", msg_string)
                article.last_status = 'dropped'
                article.save()
                continue

            # if mapper function returns successful result than update the article, and save the pickel file
            try:
                obj = Citation.step3_info(citation_object)
                article.title = obj["title"]
                article.type_of_record = obj["type"]
                article.provider_rec = obj["provider_rec"]
                article.note = 'N/A'
                article.DOI = obj["doi"]
                # Finally update the step2 record status 
                article.last_status = 'active'
                article.last_step = 3 
            
                # Create a BytesIO object to act as a file
                pkl_file = BytesIO()
                # Serialize the dictionary into the BytesIO object
                pickle.dump(citation_object, pkl_file, protocol=pickle.HIGHEST_PROTOCOL)
                pkl_file.seek(0)

                # If a file exists, delete the old file first
                if article.citation_pickle:
                    old_file_path = article.citation_pickle.path
                    if os.path.exists(old_file_path):
                        default_storage.delete(old_file_path)

                # save citaion_pickel file
                article.citation_pickle.save(
                    str(article.id)+'.pkl', 
                    File(pkl_file), 
                    save=False
                    )

                article.save()
                counter +=1
                
            except Exception as e:
                print("article id: ", article.id ," Error Messsage :", e)
 
        context = {
            'heading' : 'Message',
            'message' : f'''{counter} valid articles from step 2 successfully migrated to Step 3'''
        }

    return render(request, 'common/dashboard.html', context=context)


