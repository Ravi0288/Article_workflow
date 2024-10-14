import json
import lxml
from lxml import etree


def split_json(json_data):
    """ Splits JSON data into a list of articles as JSON strings.

    Args:
        json_data: JSON object

    Returns
        :returns: [article_json_str] (list) - list of strings:
        :returns: message (str) - if successful returns 'successful', otherwise JSON parsing error message

    """

    """ Crossref article """
    if isinstance(json_data, dict) and 'message' in json_data:
        article_json = json_data['message']
        article_json_str = json.dumps(article_json)
        return [article_json_str], 'successful'

    """submit site article collection"""
    if isinstance(json_data, list) and len(json_data) > 0 and 'submission_node_id' in json_data[0]:
        submission_string_list: list[str] = []
        for submission in json_data:
            submission_json_str = json.dumps(submission)
            submission_string_list.append(submission_json_str)
        return submission_string_list, 'successful'

    return [], 'Unknown JSON metadata'


def split_pubmed(xml_data):
    """ Splits PubMed XML data into a list of articles as JSON strings.

    Args:
        xml_data (lxml.etree.ElementTree) collection of PubMed articles

    Returns
        :returns: [article_xml_str] (list) - list of strings:
        :returns: message (str) - if successful returns 'successful'

    """
    pubmed_doctype = ''''
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE Article PUBLIC "-//NLM//DTD PubMed 3.0//EN" "https://dtd.nlm.nih.gov/ncbi/pubmed/in/PubMed.dtd">
'''

    list_of_articles: list[str] = []
    for article in xml_data:
        doc_string = etree.tostring(article, pretty_print=True)
        article_xml_str = pubmed_doctype + doc_string.decode('utf-8')
        list_of_articles.append(article_xml_str)
    return list_of_articles, 'successful'


def split_xml(xml_data, document_string):
    """Read an article collection in XML document string and split it into a list of single record XML strings.
    The XML namespaces and declaration are preserved.

    Args
        :param xml_data (lxml.etree.ElementTree) - XML document
        :param document_string (str) - XML document string
    Returns
        :returns: [article_xml_str] (list) - list of strings:
        :returns: message - if successful, otherwise error message
    """
    root = xml_data.tag

    # If single PubMED or JATS record:
    if root == 'article' or root == 'Article':
        return [document_string], 'successful'

    # If single Elsevier CONSYS record:
    if root == '{http://www.elsevier.com/xml/document/schema}document':
        return [document_string], 'successful'

    # If collection of PubMED articles:
    if root == 'ArticleSet':
        list_of_articles, message = split_pubmed(xml_data)
        return list_of_articles, message

    return [], 'Unknown XML metadata'


def get_json(my_string: str):
    try:
        data_json = json.loads(my_string)
        return data_json, 'successful'
    except (json.decoder.JSONDecodeError, ValueError) as err:
        print("json error", err)
        return None, 'JSON Error: ' + str(err)


def get_xml(my_string: str) -> lxml.etree.ElementTree:
    try:
        data_xml = etree.fromstring(my_string.encode('utf-8'))
        return data_xml, 'successful'
    except etree.XMLSyntaxError as err:
        print("xml error", err)
        return None, 'XML Error: ' + str(err)


def splitter(document_string: str):
    """Receives a JSON or XML document string containing a single or collection of article records and
       returns a list of strings with a message string.

    Args
        :param document_string (str) - String containing the JSON or XML document
    Returns
        :returns list_of_articles (list): list of article strings with JSON or XML documents
        :returns message (str) - if successful is 'successful', otherwise error message
    Notes
        :note Requires XML strings to start with "<?xml version="1.0" encoding="UTF-8"?>"
        :note Requires JSON strings to start with "{" or "["
    """
    message = ' '
    document_string = document_string.lstrip()

    # If XML string
    if document_string[:5] == "<?xml":
        data_xml, message = get_xml(document_string)
        if message == "successful":
            list_of_articles, message = split_xml(data_xml, document_string)
            return list_of_articles, message
        else:
            return [], message

    # If JSON string
    if document_string[:1] in "{[":
        data_json, message = get_json(document_string)
        if message == "successful":
            list_of_articles, message = split_json(data_json)
            return list_of_articles, message
        else:
            return [], message

    return [], 'Unknown metadata format'


import os
from django.http import HttpResponse
def test_cases(request):
    dest = 'E:\\ai\\test'
    source = 'ai\\test2'
    files = ['1.xml','2.xml','3.xml','4.xml','5.xml','6.txt','7.json']
    for item in files:
        file_path = os.path.join(dest, item)
        print(file_path)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                x = f.read()
                x = splitter(x)
                print("#####################################################################################")
                print(x[1])
                print(len(x[0]), "#############3")
        except Exception as e:
            print(e)
    return HttpResponse("done")