import json
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.conf import settings
import os
import time
import xmltodict
import re


# Function to preprocess XML text
def preprocess_xml(xml_text):
    # Escape < and > characters within text content
    return re.sub(r'(?<=>)([^<>]+)(?=<)', lambda m: m.group(0).replace('<', '&lt;').replace('>', '&gt;'), xml_text)


# funciton to write json object to json files and remove old json file
def write_json_file(json_file_path):
    if not json_file_path.endswith('.json'):
        # read the file and convert to dictionary
        with open(file=json_file_path, mode='rb') as xml_txt: 
            # replace special character
            xml_txt = xml_txt.read().replace(b'&', b'&amp;')
            json_data = xmltodict.parse(xml_txt, encoding='utf-8')

        # write as json to the same path
        with open(json_file_path[:-4] + '.json', "w") as f:
            json.dump(json_data, f)
        f.close()

        # delete the old file
        os.remove(json_file_path)
    

# segregate the file if multiple record found
def segregate_article(article_set, json_file_path):
    if article_set:
        for index, item  in enumerate(article_set):
            try:
                file_name = str(json_file_path[:-5]) + '_' + str(index+1) + '.json'
                with open(file_name, 'w') as w:
                    json.dump(item,w)
            except Exception as e:
                print(e)

    # delete the old file
    os.remove(json_file_path)

# function to check if the file has more than one record
def is_mulitple_record(json_file_path):
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            obj = data.get('ArticleSet', None)
            if obj and (len(obj) > 1):
                segregate_article(obj.get('Article', None), json_file_path)
                return True
            else:
                return False
    except Exception as e:
        print(e)


@api_view(['GET'])
def segragate_records_with_multiple_articles(request):
    for root, dirs, files in os.walk(settings.MEDIA_ROOT):
        for file_name in files:
            if file_name.endswith('.zip'):
                continue
            else:
                file_path = os.path.join(root, file_name)
                is_mulitple_record(file_path)

    return Response("execution completed")
