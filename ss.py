import requests

def download_file(url, filename):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Open the file in binary write mode and write the content
            with open(filename, 'wb') as file:
                file.write(response.content)
            print(f"File downloaded successfully as '{filename}'")
        else:
            print(f"Failed to download file. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    url = "https://journals.asm.org/doi/pdf/10.1128/AAC.29.4.720-a"
    filename = "downloaded_file.pdf"  # You can change the filename as needed
    download_file(url, filename)