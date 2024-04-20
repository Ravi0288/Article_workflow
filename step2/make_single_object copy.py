import json
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.conf import settings
import os
import time
import xmltodict


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

        # # delete the old file
        # os.remove(json_file_path)
    

# segregate the file if multiple record found


# function to check if the file has more than one record
def is_mulitple_record(json_file_path):
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
    except Exception as e:
        print(e)
    print(data)
    # if len(data) > 1:
    #     write_json_file(data, json_file_path)
    #     return True
    # else:
    #     return False


@api_view(['GET'])
def make_single_object_from_multiple(request):
    for root, dirs, files in os.walk(settings.MEDIA_ROOT):
        for file_name in files:
            if file_name.endswith('.zip'):
                continue
            else:
                file_path = os.path.join(root, file_name)
                write_json_file(file_name)

    return Response("execution completed")
