import xml.etree.ElementTree as ET
import json
from django.conf import settings
import os
from rest_framework.decorators import api_view
from rest_framework.response import Response
import zipfile
import xmltodict
from lxml import etree

# function to check if there is any zipped folder inside any directory or subdirectory
def is_any_file_zipped(source):
    # Traverse the directory tree
    for root, dirs, files in os.walk(source):
        # Check if any file in the current directory or its subdirectories is zipped
        for file_name in files:
            if file_name.endswith('.zip'):
                return True
    # If no zip file is found in any subfolder
    return False


# Function to unzip
def unzip_folders(source, destination):

    # unzip the file
    try:
        with zipfile.ZipFile(source, 'r') as zip_ref:
            zip_ref.extractall(destination)
        zip_ref.close()
        # remove the zipped file
        os.remove(source)

    except zipfile.BadZipFile:
        # Handle the case where the file is not a valid ZIP file
        os.remove(source)
    except Exception as e:
        # Handle any other unexpected exceptions
        print("An error occurred:", str(e))
        pass


def jsonify_file_content(source):
    # some file got the wrong xml format, 
    # hence caused to stop the execution. Using try except to ignore the error due to corrupted xml files
    try:
        # open file
        with open(file=source, mode='rb') as xml_txt:                 
            # replace special character
            xml_txt = xml_txt.read().replace(b'&', b'&amp;')
            json_data = xmltodict.parse(xml_txt, encoding='utf-8')

        # read the xml file and save as json to the same path
        with open(source[:-4] + '.json', "w") as f:
            json.dump(json_data, f)
        f.close()

        # remove the xml file
        os.remove(source)
    except Exception as e:
        pass


# # view to be called from api
@api_view(['GET'])
def jsonify_ftp_zipped_xml_files(request):
    while is_any_file_zipped(settings.MEDIA_ROOT):
        for root, dirs, files in os.walk(settings.MEDIA_ROOT):
            for file_name in files:
                destination =  os.path.join(root, file_name[:-4])
                source = os.path.join(root, file_name)
                if not (file_name.endswith('.zip') or file_name.endswith('.ZIP')):
                    continue
                else:
                    unzip_folders(source, destination)

    for root, dirs, files in os.walk(settings.MEDIA_ROOT):
        for file_name in files:
            destination =  os.path.join(root, file_name[:-4])
            source = os.path.join(root, file_name)
            if not file_name.endswith('.xml'):
                # some folders have got files other than xml format.
                if not file_name.endswith('.json'):
                    os.remove(source)
                    continue
            else:
                jsonify_file_content(source)

    return Response("executed process successfully")