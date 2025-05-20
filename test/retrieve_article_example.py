from create_alma_dir import create_alma_directory
import pickle
import os

# Get the base path where python file exists to creat directory
BASE_DIR = os.getcwd()

# Dictionary to store all the path required to store various files
path_directory = {
    'citation_pickel': os.path.join(BASE_DIR, 'example_data/step10_pickel.pkl'),
    'article_file' : os.path.join(BASE_DIR, 'example_data/step10_article.json'),
    'marc_file' : os.path.join(BASE_DIR, 'example_data/step10_marc.xml')
}


# Function to read the pickel file and return the citation object
def read_file():
    try:
        with open(path_directory['citation_pickel'], 'rb') as file:
            return pickle.load(file)
    except Exception as e:
        print(e)
    

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
    print(message)
    print(article_stage_dir)



if __name__ == '__main__':
    perform_action()