# find title of the json content
def main():
    import json
    json_path = "E:\\NAL-USDA\\NAL_LIBRARY_SYSTEM\\ARCHIVE_ARTICLE\\CHORUS\\12\\10.1175_jtech-d-16-0130.1.json"

    def find_key(json_obj, target_key='title'):
        if isinstance(json_obj, dict):  # Check if the object is a dictionary
            if target_key in json_obj:  # Check if the target key is present in the dictionary
                if isinstance(json_obj[target_key], dict):
                    try:
                        print(json_obj[target_key]['#text'])
                        return json_obj[target_key]['#text']
                    except Exception as e:
                        print(str(json_obj[target_key]))
                        return str(json_obj[target_key])
            for value in json_obj.values():
                find_key(value, target_key)  # Recursively search through the dictionary values
        elif isinstance(json_obj, list):  # Check if the object is a list
            for item in json_obj:
                find_key(item, target_key)  # Recursively search through the list items

    with open(json_path, 'rb') as f:
        json_obj = json.load(f)
        find_key(json_obj=json_obj)

if __name__ == '__main__':
    main()