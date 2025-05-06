import os
import shutil
from typing import Tuple
from .retrieve_article_manuscript import retrieve_manuscripts

# Function to created directory
def create_directory(path: str) -> None:
    # Create a directory if it doesn't already exist
    # dir_path = base + path
    os.makedirs(path, exist_ok=True)


# Determine top level directory
def determine_top_level_directory(citation_object, base: dict) -> str:
    # Determine the correct top-level folder based on citation source and status
    is_usda = citation_object.local.USDA
    has_mmsid = bool(citation_object.local.identifiers.get('mmsid'))

    # Actions based on if article is usda_funded or not
    if is_usda:
        return os.path.join(base, 'ARTICLE_STAGING/MERGE_USDA') if has_mmsid else os.path.join(base, 'ARTICLE_STAGING/NEW_USDA')
    else:
        return os.path.join(base, 'ARTICLE_STAGING/MERGE_PUBLISHER') if has_mmsid else os.path.join(base, 'ARTICLE_STAGING/NEW_PUBLISHER')



# Function to copy file
def copy_file(source: str, destination: str) -> None:
    # Copy a file from source to destination.
    if source and os.path.exists(source):
        shutil.copy2(source, destination)



# Function for staging metadata
def stage_metadata_files(citation_object, path_directory: dict, target_folder: str, base: str) -> None:
    # Copy metadata files into the citation folder
    is_usda = citation_object.local.USDA

    # Get Citation pickle file
    try:
        pickle_src = path_directory.get('citation_pickle')
        pickle_dst = os.path.join(
            target_folder,
            'usda-citation.pkl.txt' if is_usda else 'publisher-citation.pkl.txt'
        )
        copy_file(pickle_src, pickle_dst)
    except Exception as e:
        print(e)

    # Get article file
    article_file = path_directory.get('article_file')
    article_dst = os.path.join(
        target_folder,
        'usda-source.xml' if is_usda else 'publisher-source.xml'
    )
    copy_file(article_file, article_dst)

    # Get MARC file
    marc_src = path_directory.get('marc_file')
    marc_dst = os.path.join(target_folder, 'marc.xml')
    copy_file(marc_src, marc_dst)



# Main function to create the Alma folder structure, and copy all article, citation, marc and manuscript file
def create_alma_folder(citation_object, base: str, path_directory: dict) -> list:

    # Step 1: Determine top-level folder
    top_level_folder = determine_top_level_directory(citation_object, base)

    # Step 2: Build citation folder path with pid
    pid = citation_object.local.identifiers.get('pid')
    if not pid:
        return "Missing PID in citation object", citation_object

    f_name = 'agid-' + str(pid)
    citation_folder = os.path.join(top_level_folder, f_name)

    # Step 3: Create directory if not exists
    create_directory(citation_folder)

    # Step 4: Stage the metadata files
    stage_metadata_files(citation_object, path_directory, citation_folder, base)

    # Step 5: Retrieve manuscript and support files (for USDA only)
    if citation_object.local.USDA:
        manuscript_file = citation_object.resource.primary
        support_files = citation_object.resource.secondary

        message = retrieve_manuscripts(citation_folder, manuscript_file, support_files)
        # message = retrieve_manuscripts(citation_folder, manuscript_file, support_files)

        if message != "success":
            if citation_object.local.cataloger_notes is None:
                citation_object.local.cataloger_notes = []

            # Add message to cataloger notes
            cataloger_notes = getattr(citation_object.local, 'cataloger_notes', '')
            citation_object.local.cataloger_notes = cataloger_notes.append(message.strip())
            citation_object.status = "review"

            return message, citation_object

    return "successful", citation_object