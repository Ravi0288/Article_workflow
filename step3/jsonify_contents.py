from rest_framework.decorators import api_view
from django.conf import settings
import os
import xmltodict
import json


@api_view(['GET'])
def jsonify_xml_file(request):
    for root, dirs, files in os.walk(settings.ARTICLE_ROOT):
        for file_name in files:
            # some file got the wrong xml format, 
            # hence caused to stop the execution. Using try except to ignore the error due to corrupted xml files
            if file_name.endswith('.xml'):
                try:
                    # open file
                    with open(file=file_name, mode='rb') as xml_txt:                 
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
                    with open(file_name[:-4] + '.json', "w") as f:
                        json.dump(json_data, f)
                    f.close()

                    # remove the xml file
                    os.remove(file_name)
                except Exception as e:
                    pass