import re

# at many places xml file title having incorrect or special symbols.
# Function to remove speccial characters that are causing exception while storing to db
def remove_incorrect_values(input_string):
    # Define a regular expression pattern to match non-alphanumeric characters
    if isinstance(input_string, str):
        input_string.replace('\u2010;', '-').replace('&#x2019;', '-')
        pattern = re.compile(r'[^a-zA-Z0-9\s]')  # Keep letters, numbers, and spaces

        # Use the pattern to substitute non-alphanumeric characters with an empty string
        cleaned_string = re.sub(pattern, '', input_string)
        return str(cleaned_string)
    return input_string



# XML files received from multiple sources may have different strucutre.
# Nested looping / traversing of JSON failes with unknown reson. Hence listing the known types

# This function need through testing. After multiple try due to incorrect formate in json this function fails sometime
# That is why know format of the jsons are listed
def travers_json_for_title(json_obj):
    try:
        if isinstance(json_obj, dict):
            if 'title' in json_obj:
                # return escape(json_obj['title'])
                if isinstance(json_obj['title'], str):
                    print(json_obj['title'])
                    return remove_incorrect_values(json_obj['title'].strip())
                
                if isinstance(json_obj['title'], dict):
                    print(json_obj['title'])
                    # XML files received from FTP are having title as dictionary
                    return remove_incorrect_values(json_obj['title']['#text'].strip())
                elif isinstance(json_obj['title'], list):
                    print(json_obj['title'])
                    # XML files received from cross ref are of type list
                    return remove_incorrect_values(json_obj['title'][0].strip())                 
                else:
                    print(json_obj['title'])
                    return remove_incorrect_values(json_obj['title'].strip())
            for value in json_obj.values():
                find_title(value)
        elif isinstance(json_obj, list):
            for item in json_obj:
                find_title(item)
    except Exception as e:
        print(e)
        return None




# find title of the json content
def find_title(json_obj):

    try:
        return remove_incorrect_values(json_obj['back']['ref-list']['ref'][0]['element-citation']['article-title'].strip())
    except Exception as e:
        pass

    try:
        return remove_incorrect_values(json_obj['back']['ref-list']['ref'][0]['element-citation']['article-title']['#text'].strip())
    except Exception as e:
        pass

    try:
        return remove_incorrect_values(json_obj['front']['journal-meta']['journal-title-group']['journal-title'].strip())
    except Exception as e:
        pass

    try:
        return remove_incorrect_values(json_obj['back']['ref-list']['ref'][0]['element-citation']['article-title'].strip())
    except Exception as e:
        pass

    try:
        return remove_incorrect_values(json_obj['article']['front']['article-meta']['title-group']['article-title'].strip())
    except Exception as e:
        pass

    try:
        return remove_incorrect_values(json_obj['front']['article-meta']['title-group']['#text'].strip())
    except Exception as e:
        pass

    try:
        # in some files this is the structure of title
        return remove_incorrect_values(json_obj['front']['titlegrp']['title'].strip())
    except Exception as e:
        pass

    try:
        # in some files this is the structure of title
        return remove_incorrect_values(json_obj['front']['titlegrp']['title']['#text'].strip())
    except Exception as e:
        pass

    try:
        # in some files this is the structure of title
        return remove_incorrect_values(json_obj['message']['title'].strip())
    except Exception as e:
        pass

    try:
        # in some files this is the structure of title
        return remove_incorrect_values(json_obj['message']['title'][0].strip())
    except Exception as e:
        pass

    try:
        # in some files this is the structure of title
        return remove_incorrect_values(json_obj['title'].strip())
    except Exception as e:
        pass

    try:
        # in some files this is the structure of title
        return remove_incorrect_values(json_obj['article']['front']['article-meta']['title-group']['article-title']['#text'].strip())
    except Exception as e:
        pass

    return None
