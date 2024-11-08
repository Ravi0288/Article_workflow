import xml.etree.ElementTree as ET
import json
import os

def validate_xml(file_path):
    try:
        tree = ET.parse(file_path)
        tree.getroot()
        print("Valid XML")
    except ET.ParseError:
        print("Invalid XML")

def validate_json(file_path):
    try:
        with open(file_path, 'r') as file:
            json.load(file)
        print("Valid JSON")
    except json.JSONDecodeError:
        print("Invalid JSON")

def validate_file(file_path):
    if file_path.endswith('.xml'):
        validate_xml(file_path)
    elif file_path.endswith('.json'):
        validate_json(file_path)
    else:
        print("Unsupported file format")

# Example usage:
file_path = 'path/to/your/file.xml'  # Replace with your file path

for root, dir, file in os.walk('E:/ai/metadata/ARTICLES'):
    validate_file(os.path.join(root, file))
