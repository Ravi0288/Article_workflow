import requests
import os

def perform_network_connection_check():
    url_list = []
    
    endpoints = {
        "https://www.doi.org/",
        "https://na91.alma.exlibrisgroup.com/view/sru/01NAL_INST",
        os.getenv("SOLR_PING")
    }

    for url in endpoints:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            url_list.append(url)

    return url_list
