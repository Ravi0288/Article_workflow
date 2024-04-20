import json
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.conf import settings
import os
import time


# funciton to write json object to json files and remove old json file
def write_json_file(json_content, json_file_path):
    # iterate through the json object, write each json to new file and name the file as file_name_part
    for index, obj in enumerate(json_content):
        if not json_file_path.endswith('.json'):
            continue

        print(obj)

        # try:
        #     file_name = json_file_path[:-5] + '_' + str(index+1) + '.json'
        #     with open(file_name, 'w') as f:
        #         json.dump(obj, f)
        #         f.close()
        # except Exception as e:
        #     print(e)
    # delete the old file
    # os.remove(json_file_path)
    


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
            
            is_mulitple_record(file_path)

    return Response("execution completed")
