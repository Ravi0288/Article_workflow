from rest_framework.decorators import api_view
from django.conf import settings
import os
import xmltodict
import json
from .common.find_doi import find_doi
from .common.find_title import find_title
from model.article import Article_attributes, Jsonified_articles


@api_view(['GET'])
def jsonify_xml_file(request):
    articles = Article_attributes.objects.filter(last_step=2)
    for item in articles:
        qs=Jsonified_articles.objects.filter(article_attributes=item.id)
        if(qs.exists()):
            # update_record(item.article_file)
            pass
            # than update the file
        else:
            # create new record
            if item.article_file.filename.endswith('.xml'):
                try:
                    # open file
                    with open(file=item.article_file, mode='rb') as xml_txt:                 
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
                    new_file = item.article_file.filename[:-4] + '.json'
                    with open(new_file, "w") as f:
                        json.dump(json_data, f)
                    f.close()

                    Jsonified_articles.create('data')
                except Exception as e:
                    pass



# def update_record(file_path):
#     for item in articles:
#         qs = articles.filter(article_file=file)[0]
#         with open(file, 'r') as f:
#             data = json.load(file)
#         try:
#             qs.title = find_title(data)
#             qs.DOI = find_doi(data)
#             qs.last_step = 3
#             qs.note = 'ok'
#             qs.provider_rec = 'node_450'
#             qs.type_of_record = 'article' 
#             qs.save()
#             f.close()
#         except Exception as e:
#             qs.status = 'failed'
#             qs.note = e
#             qs.save()

