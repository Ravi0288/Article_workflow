from rest_framework.decorators import api_view
from django.conf import settings
import os
import xmltodict
import json
from .common.find_doi import find_doi
from .common.find_title import find_title
from model.article import Article_attributes, Jsonified_articles
from django.contrib.auth.decorators import login_required
from django.shortcuts import render



def process_file(article, new_file_path):
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

            # with open(new_file_path, 'r') as f:
            #     file_content = f.read()
            # f.close()

            return file_content
        except Exception as e:
            article.note = e
            article.save()
            return False

    else:
        with open(article.article_file.path, 'r') as f:
            file_content = f.read()
            f.close()


@login_required
@api_view(['GET'])
def jsonify_xml_file(request):
    articles = Article_attributes.objects.filter(last_status='active')
    for article in articles:
        qs=Jsonified_articles.objects.filter(article_attributes=article.id)
        if(qs.exists()):
            new_file = (article.article_file.name[:-4] + '.json').replace('ARTICLES','PROCESSED_ARTICLES')
            # create new record
            file_content = process_file(article, new_file)

            qs.article_file = new_file,
            qs.journal = '',
            qs.title = find_title(file_content),
            qs.type_of_record = article.type_of_record,
            qs.article_attributes = article.id,
            qs.note = 'ok',
            qs.DOI = find_doi(file_content),
            qs.save()

            article.last_status = 'completed'
            article.last_step = 2 
            article.save()

        else:
            new_file = (article.article_file.name[:-4] + '.json').replace('ARTICLES','PROCESSED_ARTICLES')
            # create new record
            file_content = process_file(article, new_file)

            if file_content:
                Jsonified_articles.create(
                    article_file = new_file,
                    journal = '',
                    title = find_title(file_content),
                    type_of_record = article.type_of_record,
                    article_attributes = article.id,
                    note = 'ok',
                    DOI = find_doi(file_content),
                )
                article.last_status = 'completed'
                article.save()

    context = {
        'heading' : 'Message',
        'message' : 'All valid articles successfully migrated to step-3'
    }

    return render(request, 'common/dashboard.html', context=context)


