
# find doi function to find doi
def find_doi(json_obj):

    try:
        return json_obj['front']['pubfront']['doi']
    except:
        pass

    try:
        return json_obj['DOI']
    except:
        pass 

    try:
        return json_obj['message']['DOI']
    except:
        pass

    try:
        for item in json_obj['front']['article-meta']['article-id']:
            if item['@pub-id-type'] == 'doi':
                return item['#text']
    except Exception as e:
        pass

    try:
        for item in json_obj['article']['front']['article-meta']['article-id']:
            if item['@pub-id-type'] == 'doi':
                return item['#text']
    except Exception as e:
        pass

    try:
        for item in json_obj['front']['article-meta']['article-id']:
            if item['@pub-id-type'] == 'doi':
                return item['#text']
    except Exception as e:
        pass

    return None
