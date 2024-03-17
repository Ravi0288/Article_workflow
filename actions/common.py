import os
import requests
import zipfile


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


# function to return the folder size on FTP.
# Since in FTP we don't have build in function to read folder size hence we need to iterate
# each file in the folder and sum the size that becomes the size of the folder
def get_folder_size_on_ftp(connect, folder):
    size = 0
    try:
        connect.cwd(folder)
        files = connect.nlst()
        for file in files:
            try:
                size += connect.size(file)
            except:
                size += get_folder_size_on_ftp(connect, file)
        connect.cwd('..')
        return size
    except Exception as e:
        return 0


# function to unzip the file
def unzip_files(file_content):
    try:
        with zipfile.ZipFile(file_content, 'r') as zip_ref:
            # Extract the contents of the zip file
            filepath =(file_content.name).split('.')
            zip_ref.extractall(filepath[0])
            return True
    except Exception as e:
        return False


# download folder from FTP


# function to save file content
def download_file(filename, temp_dir, instance):
    filename = os.path.join(temp_dir, instance.strip())
    with open(filename, 'wb') as f:
        f.write(requests.get(instance.url).content)
    return


# function to iterate folder. If another folder found in side the folder this function will call itself.
# if file found this will download the file
def download_folder(ftp_connection, article, instance):
    ftp_connection.cwd(article)
    filenames = ftp_connection.nlst()
    for filename in filenames:
        if '.' in filename:  # It's a file
            download_file(ftp_connection, filename, instance)
        else:  # It's a subfolder
            download_folder(ftp_connection, article, os.path.join(article, article))
    ftp_connection.cwd('..')
    return

