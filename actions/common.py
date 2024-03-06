import os
import time
from rest_framework.response import Response


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



# function to merge read, write and delete operations
def action(inputfile, outputfile):
    # Replace 'input.txt' with the path to your text file
    input_file_path = inputfile 
    output_file_path = outputfile
    # Read the content of the file
    print("Reading file content")
    file_content = read_file(input_file_path)
    time.sleep(1)
    print(file_content)
    time.sleep(1)

    print("Saving file")
    time.sleep(1)
    # Save the content as a new file
    save_blob_as_file(file_content, output_file_path)
    print(f"\nBlob saved as '{output_file_path}'.")

    return output_file_path


