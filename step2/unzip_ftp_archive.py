import xml.etree.ElementTree as ET
import json
from django.conf import settings
import os
from rest_framework.decorators import api_view
from rest_framework.response import Response
import zipfile
import xmltodict
from lxml import etree


# Function to remove all the files of provided extension
def remove_files(extension, path):
    files = os.listdir(path+extension)
    for item in files:
        os.remove(item)


# Function to unzip
def unzip_folders(zip_file, extract_to):

    # unzip the file
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    zip_ref.close()
    # remove the zipped file
    os.remove(zip_file)


# view to be called from api
@api_view(['GET'])
def jsonify_ftp_zipped_xml_files(request):
    # get root all ftp filders from article_library
    folders = os.listdir(settings.MEDIA_ROOT)
    ftp_folders = [x for x in folders if x not in ['SUBMISSION','CROSSREF','CHORUS']]

    # iterting through all the folders 
    for item in ftp_folders:

        # get all the zipped files and iterate through it
        zip_file_path = os.path.join(settings.MEDIA_ROOT, item)
        zipped_files = os.listdir(zip_file_path)
        for zipped_file in zipped_files:
            # if file is not a zip_file do nothing 
            if not zipped_file.endswith('.zip'):
                continue

            file_path = os.path.join(zip_file_path, zipped_file)
            # unzipe the file
            unzip_folders(os.path.join(file_path),file_path[:-4])


            # preparing the path for xml
            xml_files = os.listdir(file_path[:-4])

            # iterate through all the xml file in the selected directory
            for xml_file in xml_files:
                # make the file path
                xml_file_path = os.path.join(file_path[:-4],xml_file)

                # some folders have got files other than xml format.
                if not xml_file.endswith('.xml'):
                    os.remove(xml_file_path)

                # some file got the wrong xml format, 
                # hence caused to stop the execution. Using try except to ignore the error due to corrupted xml files
                try:

                    # open file
                    with open(file=xml_file_path, mode='rb') as xml_txt:                 
                        json_data = xmltodict.parse(xml_txt, encoding='utf-8')
                    xml_txt.close()

                    # read the xml file and save as json to the same path
                    with open(xml_file_path[:-4] + '.json', "w") as f:
                        json.dump(json_data, f)
                    f.close()

                    # remove the xml file
                    os.remove(xml_file_path)
                except Exception as e:
                    pass

    return Response("successfull")
