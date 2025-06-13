import os
import configparser

def get_aws_credentials(profile_name='default'):

    # Expand the ~ to the full home directory path
    credentials_path = os.path.expanduser('~/.aws/credentials')
    
    if not os.path.exists(credentials_path):
        return False, f"AWS credentials file not found at {credentials_path}"
    
    config = configparser.ConfigParser()
    config.read(credentials_path)
    
    if profile_name not in config:
       return False, f"Profile '{profile_name}' not found in credentials file"
    
    profile = config[profile_name]
    
    try:
        access_key = profile['aws_access_key_id']
        secret_key = profile['aws_secret_access_key']
    except KeyError as e:
        return False, f"Missing required key {str(e)} in profile '{profile_name}'"
    
    return access_key, secret_key