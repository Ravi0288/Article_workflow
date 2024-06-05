from rest_framework.decorators import api_view
from django.conf import settings
import os
import xmltodict
import json
from .common.find_doi import find_doi
from .common.find_title import find_title
from model.article import Article_attributes


@api_view(['GET'])
def jsonify_xml_file(request):
    articles = Article_attributes.objects.filter(last_stage=2)
    for root, dirs, files in os.walk(settings.ARTICLE_ROOT):
        for file in files:
            # some file got the wrong xml format, 
            # hence caused to stop the execution. Using try except to ignore the error due to corrupted xml files
            if file.endswith('.xml'):
                try:
                    # open file
                    with open(file=file, mode='rb') as xml_txt:                 
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
                    new_file = file[:-4] + '.json'
                    with open(new_file, "w") as f:
                        json.dump(json_data, f)
                    f.close()
                    qs = articles.filter(article_file=new_file)[0]
                    qs.article_file = new_file   
                    qs.save() 

                    # remove the xml file
                    os.remove(file)
                except Exception as e:
                    pass


@api_view(['GET'])
def update_fields(request):
    data_source = settings.ARTICLE_ROOT
    articles = Article_attributes.objects.filter(last_stage=2, status='completed')
    for root, dirs, files in os.walk(data_source):
        for file in files:
            qs = articles.filter(article_file=file)[0]
            with open(file, 'r') as f:
                data = json.load(file)
            try:
                qs.title = find_title(data)
                qs.DOI = find_doi(data)
                qs.last_stage = 3
                qs.note = 'ok'
                qs.provider_rec = 'node_450'
                qs.type_of_record = 'article' 
                qs.save()
                f.close()
            except Exception as e:
                qs.status = 'failed'
                qs.note = e
                qs.save()

