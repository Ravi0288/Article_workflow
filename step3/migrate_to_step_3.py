from rest_framework.decorators import api_view
import xmltodict
import json
from .common.find_doi import find_doi
from .common.find_title import find_title
from model.article import Article_attributes, Article
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


# Function to read xml / json file in utf-8 mode. This function will return the content of the file
def read_and_return_file_content(article, new_file_path):
    if article.article_file.name.endswith('.xml'):
        try:
            # open file
            with open(file=article.article_file.path, mode='rb') as xml_txt:                 
                # replace special character
                xml_txt = xml_txt.read().replace(
                    b'&#x2018;', b'"').replace(
                        b'&#8216;',b'"').replace(
                            b'&lsquo;',b'"').replace(
                                b'i', b'&iacute;').replace(
                                    b'&', b'&amp;').replace(
                                        b'<i>',b''
                                    )
                # xml_txt = preprocess_xml(xml_txt)
                json_data = xmltodict.parse(xml_txt, encoding='utf-8')

            # read the xml file and save as json to the same path
            file_content = ''
            with open(new_file_path, "w") as f:
                json.dump(json_data, f)
                file_content = f.read()
            f.close()
            return file_content
        
        except Exception as e:
            article.note = e
            article.save()
            return False

    else:
        with open(article.article_file.path, 'r', encoding='utf-8') as f:
            file_content = f.read()
            f.close()
        return file_content        


@login_required
@api_view(['GET'])
def jsonify_xml_file(request):
    step2_articles = Article_attributes.objects.filter(last_status='active').filter(provider__in_production=True)
    for article in step2_articles:
        qs=Article.objects.filter(article_attributes=article.id)

        # if file already exists, compare and update
        if(qs.exists()):
            new_file = (article.article_file.name[:-4] + '.json').replace('ARTICLES','JSONIFIED_ARTICLES')

            # create new record
            # read_and_return_file_content function to be updated with Chuck functions
            file_content = read_and_return_file_content(article, new_file)

            # field values to be updated from the function Citation.step3_info()
            qs.article_file = new_file,
            qs.journal = '',
            qs.title = find_title(file_content),
            qs.type_of_record = article.type_of_record,
            qs.article_attributes = article.id,
            qs.note = 'ok',
            qs.DOI = find_doi(file_content),
            qs.save()
            ########################

            article.last_status = 'completed'
            article.last_step = 3 
            article.save()

        # if file is new, create new record
        else:
            new_file = (article.article_file.name[:-4] + '.json').replace('ARTICLES','JSONIFIED_ARTICLES')
            # create new record
            file_content = read_and_return_file_content(article, new_file)

            if file_content:
                Article.create(
                    article_file = new_file,
                    journal = '',
                    title = find_title(file_content),
                    type_of_record = article.type_of_record,
                    article_attributes = article.id,
                    note = 'ok',
                    DOI = find_doi(file_content),
                )
                article.last_status = 'completed'
                article.last_step = 3
                article.save()

    context = {
        'heading' : 'Message',
        'message' : 'All valid articles from step 2 successfully migrated to step-3'
    }

    return render(request, 'common/dashboard.html', context=context)


