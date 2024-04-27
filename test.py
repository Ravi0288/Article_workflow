# find title of the json content
def main():
    import json
    json_path = "E:\\NAL-USDA\\NAL_LIBRARY_SYSTEM\\ARTICLES\\CSIRO\\AM_39_1\\AM16013abs_lBG9pXl.json"
    def find_key(json_obj, target_key='title'):
        try:
            for key, value in json_obj.items():
                # Check if the key is a potential title candidate
                if key.lower() == 'title':
                    # Assume the title is a string value
                    if isinstance(value, str):
                        return print(value)

                    elif isinstance(value, dict):
                        nested_title = find_key(value)
                        if nested_title:
                            return nested_title

            # Check if the title is not found at root
            if isinstance(json_obj, dict):
                # Check if the target key is present in the dictionary
                if 'title' in json_obj:
                    if isinstance(json_obj['title'], dict):
                        # this is added as per observation files received from FTP. these files have object for its title and actual 
                        # text is stored under #text key.
                        print(json_obj['title']['#text'])
                for value in json_obj.values():
                    # Recursively search through the dictionary values
                    find_key(value)

            # Check if the object is a list 
            elif isinstance(json_obj, list):
                for item in json_obj:
                    # Recursively search through the list items
                    find_key(item)
            return None
        except Exception as e:
            return None

    with open(json_path, 'rb') as f:
        json_obj = json.load(f)
        find_key(json_obj=json_obj)

if __name__ == '__main__':
    main()