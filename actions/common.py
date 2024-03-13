import os
import time
from rest_framework.response import Response
import requests


# Function to read the file
# This function will take file path as input and will return the file content    
def read_file(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        return content
    except Exception as e:
        print("File not found")
        raise e
    

# Function to save the file
# This function will take blob and file_name to save the blob with file_name
def save_blob_as_file(blob, output_file_path):
    with open(output_file_path, 'w') as output_file:
        output_file.write(blob)


# function to delete file by given path
def delete_file(file_path):
    try:
        os.remove(file_path)
        print(f"File '{file_path}' deleted successfully.")
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print(f"Error deleting file '{file_path}': {e}")



# function to check downloaded content is file or folder on API
def is_api_content_folder(url):
    response = requests.head(url)  # Send a HEAD request to retrieve headers only
    content_type = response.headers.get('Content-Type', '')
    if 'text/html' in content_type:
        return True
    else:
        return False


# function to check the given path content is file or folder on FTP 
def is_ftp_content_folder(connect, path):
        try:
            connect.cwd(path)
            return True
        except Exception as e:
            return False




