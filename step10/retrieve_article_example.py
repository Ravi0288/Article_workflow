from create_alma_dir import create_alma_directory
import pickle
import os

# Dictionary to store all the path required to store various files
path_directory = {
    'CITATION_PICKEL': 'example_data/step10_pickel.pkl',
    'ARTICLE_FILE' : 'example_data/step10_article.json',
    'MARC_FILE' : 'example_data/step10_marc.xml'
}

# Get the base path where python file exists to creat directory
BASE_DIR = os.getcwd()


# Function to read the pickel file and return the citation object
def read_file():
    with open(path_directory['CITATION_PICKEL'], 'rb') as file:
        return pickle.load(file)
    

def perform_action():
    # read citation file
    citation_object = read_file()
    
    '''
    1: Call create_alma_directory function.
    2: This function will create all the required directories / subdirectories and 
        pull the manuscript file from the availbalbel URLs.
    3: create_alma_directory function internally calls retrieve_manuscripts function to retreive and save the manuscript file
        in specified directory.
    4: Once run, create_alma_directory function will return status message (Error occured or executed successfully),
        citation_object, and path to directory created for staging the article.
    '''

    message, citation_object, article_stage_dir = create_alma_directory(citation_object, BASE_DIR, path_directory)
    print("Executed successfully")


if __name__ == '__main__':
    perform_action()