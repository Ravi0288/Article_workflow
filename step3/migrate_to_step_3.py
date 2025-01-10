import mapper
from rest_framework.decorators import api_view
from model.article import Article_attributes, Article
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from metadata_routines.citation import Citation
from django.core.files import File
from io import StringIO


# Function to read xml / json file in utf-8 mode. This function will return file content
def read_and_return_file_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        file_content = f.read()
        f.close()
    return file_content        


# Main function to migrate Step 2 files to Step 3
@login_required
@api_view(['GET'])
def jsonify_xml_file(request):

    # Fetch all files that need to be processed from Article_attributes table
    step2_articles = Article_attributes.objects.filter(
        last_status='active', 
        provider__in_production=True, 
        last_step=2
        )
    print(step2_articles.count(), " Article attributes found to be processed for step 3")

    # Process each record from article-attributes
    for item in step2_articles:
        qs=Article.objects.filter(article_attributes__id=item.id)

        # if article found against given article_attributes_id, 
        # but article_atrribute contents are not changed. continue to next recrod
        if qs.exists() and not item.is_content_changed:
            print("article found and no change detected in step 2. Skiping this iteration")
            continue

        # read and return file content in utf-8 format
        file_content = read_and_return_file_content(item.article_file.path)
        # read and return citation_object
        citation_object, msg_string = mapper.mapper(file_content, item.provider.source_schema) 

        # if mapper function returns unsuccessful result, 
        # just delete the newly created file, update the status and continue to next article
        if msg_string != 'successful':
            print("Mapper function returned = '", msg_string, "'. Skiping this iteration")
            item.last_status = 'failed'
            item.save()
            continue

        # if mapper function returns successful result than continue
        obj = Citation.step3_info(citation_object)

        # prepare file name and content to be stored in article
        new_file = (item.article_file.name).replace('ARTICLES','PROCESSED_ARTICLES')
        file_content = File(file_content)
        # file_content = StringIO(File(file_content))

        # if article found against given article_attributes_id  
        if qs.exists():
            # and the article_attribute contents are found changed,update the existing Article
            if item.is_content_changed:
                print("Article exists and the content of the article found changed in step 2.")
                qs[0].journal = '',
                qs[0].title = obj["title"],
                qs[0].type_of_record = obj["type"],
                qs[0].article_attributes = item.id,
                qs[0].provider_rec = obj["provider_rec"],
                qs[0].note = None,
                qs[0].DOI = obj["doi"],
                qs[0].article_file.save(new_file, file_content)
            
            # in case no changes found, skip this iteration and move to next record 
            else:
                continue


        # if no article found against the given article_attributes_id and valid file content is found, create new article
        else:
            if file_content:
                print("Creating new article")
                new_article = Article()
                new_article.journal = '',
                new_article.title =  obj["title"],
                new_article.type_of_record = obj["type"],
                new_article.article_attributes = item.id,
                new_article.provider_rec = obj["provider_rec"],
                new_article.note = None,
                new_article.DOI = obj["doi"],
                new_article.article_file.save(new_file, file_content)

            # if null file content is found, do nothing
            else:
                print("file content not found or is None")
                continue

        # Finally update the step2 record status 
        item.last_status = 'completed'
        item.last_step = 3 
        item.save()
        print("last status of article_attributes updated. Finished. Going to next iteration")

    context = {
        'heading' : 'Message',
        'message' : 'All valid articles from Step 2 have been successfully migrated to Step 3'
    }

    return render(request, 'common/dashboard.html', context=context)


