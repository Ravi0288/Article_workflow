import os
import boto3
import logging
from botocore.exceptions import BotoCoreError, ClientError
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class AlmaS3Uploader:

    # Initialize the values
    def __init__(self, staging_info):
        self.s3_uris = staging_info["s3_uris"]
        self.aws_access_key = staging_info["aws_access_key"]
        self.aws_secret_key = staging_info["aws_secret_key"]
        self.base_s3_uri = staging_info["base_s3_uri"]
        self.bucket = staging_info["bucket"]
        self.prefix = staging_info["prefix"]
        self.base_path = staging_info["base_path"]

        # Connect to S3
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key
        )


    # Create requied directories
    def create_s3_directories(self):
        """
        Creates empty '.keep' files in each directory under the base prefix.
        This is required because the direcotry will not exists without having at least a single file in it
        """
        for name, relative_path in self.s3_uris.items():
            # Full prefix under base path
            prefix = f"{self.prefix.rstrip('/')}/{relative_path.strip('/')}/"
            key = f"{prefix}.keep"
            try:
                # create directory and place .keep file inside it
                self.s3.put_object(Bucket=self.bucket, Key=key, Body=b'')
            except (BotoCoreError, ClientError) as e:
                return False, e
        return True, 'Successful'

    # Check if there is any content in bucket except .keep file
    def check_s3_buckets_empty(self):
        for name, relative_path in self.s3_uris.items():
            prefix = f"{self.prefix.rstrip('/')}/{relative_path.strip('/')}/"
            response = self.s3.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
            contents = response.get("Contents", [])

            # Ignore if the only file is the .keep placeholder
            actual_files = [obj for obj in contents if not obj['Key'].endswith('.keep')]

            if actual_files:
                # Non-placeholder file found
                return False
            
        # All directories are empty except for .keep
        return True

    # Empty the S3 bucket
    def empty_s3_bucket(self):
        for uri in self.s3_uris:
            bucket, prefix = self.bucket, self.prefix
            response = self.s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
            objects = [{'Key': obj['Key']} for obj in response.get('Contents', [])]
            if objects:
                self.s3.delete_objects(Bucket=bucket, Delete={'Objects': objects})
        return True, 'Successful'
    
    # Upload the files from each directory to S3
    def upload_directory_to_alma_s3(self): 
        s3_paths = self.s3_uris
        bucket = self.bucket
        base_path = self.base_path

        def upload_file(local_path, s3_key):
            full_s3_key = f"{self.prefix.rstrip('/')}/{s3_key.lstrip('/')}"
            try:
                self.s3.upload_file(local_path, bucket, full_s3_key)
            except Exception as e:
                print(f"Failed to upload {local_path} → s3://{bucket}/{full_s3_key}: {e}")
                return False, e

        # 1. Upload NEW_USDA
        new_usda_dir = os.path.join(base_path, 'NEW_USDA').replace('\\', '/')
        for root, dir, files in os.walk(new_usda_dir):
            for file in files:
                local_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_path, new_usda_dir).replace("\\", "/")
                s3_key = s3_paths['new_usda_record'] + relative_path
                upload_file(local_path, s3_key)

        # 2. Upload NEW_PUBLISHER
        new_sub_dir = os.path.join(base_path, 'NEW_PUBLISHER')
        for root, dir, files in os.walk(new_sub_dir):
            for file in files:
                local_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_path, new_sub_dir).replace("\\", "/")
                s3_key = s3_paths['new_submission_records'] + relative_path
                upload_file(local_path, s3_key)

        # 3. Upload MERGE_USDA (with and without digital content)
        merge_usda_dir = os.path.join(base_path, 'MERGE_USDA')
        for root, dir, files in os.walk(merge_usda_dir):
            for file in files:
                local_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_path, merge_usda_dir).replace("\\", "/")
                if file.lower() == 'marc.xml':
                    s3_key = s3_paths['merge_usda_without_digital_files'] + relative_path
                    upload_file(local_path, s3_key)
                s3_key = s3_paths['merge_usda_with_digital_files'] + relative_path
                upload_file(local_path, s3_key)

        # 4. Upload MERGE_PUBLISHER (with and without digital content)
        merge_sub_dir = os.path.join(base_path, 'MERGE_PUBLISHER')
        for root, dir, files in os.walk(merge_sub_dir):
            for file in files:
                local_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_path, merge_sub_dir).replace("\\", "/")
                if file.lower() == 'marc.xml':
                    s3_key = s3_paths['new_submission_without_digital_files'] + relative_path
                    upload_file(local_path, s3_key)
                s3_key = s3_paths['new_submission_with_digital_files'] + relative_path
                upload_file(local_path, s3_key)

        return True, 'Successful'