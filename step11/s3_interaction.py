import os
import boto3
import shutil
import zipfile
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class AlmaS3Uploader:
    def __init__(self, staging_info):
        self.staging_folder = staging_info["folder_path"]
        self.folder_type = staging_info["type"]  # "new" or "merge"
        self.min_required_files = staging_info["min_files"]
        self.s3_uris = staging_info["s3_uris"]  # list of S3 URIs
        self.archive_path = staging_info["archive_path"]
        self.active = staging_info["active"]
        self.bucket_empty_check = staging_info["bucket_empty_check"]
        self.aws_access_key = staging_info["aws_access_key"]
        self.aws_secret_key = staging_info["aws_secret_key"]
        self.base_s3_uri = staging_info["base_s3_uri"]

        self.s3 = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key
        )

    def run(self):
        report = {
            "staging_folder": self.staging_folder,
            "upload_time": str(datetime.now()),
            "uploaded_count": 0,
            "archive_location": "",
            "errors": [],
            "warnings": []
        }

        try:
            if not self.active:
                report["warnings"].append("Folder is inactive.")
                return report

            if not self._check_min_files():
                report["warnings"].append("Not enough files to upload.")
                return report

            if not self._check_s3_buckets_empty():
                report["warnings"].append("S3 buckets are not empty.")
                return report

            uploaded_count = self._upload_to_s3()

            if uploaded_count == 0:
                report["errors"].append("No files uploaded.")
                return report

            archive_file = self._archive_staging_folder()
            self._cleanup_local_folder()

            report["uploaded_count"] = uploaded_count
            report["archive_location"] = archive_file

        except Exception as e:
            logger.error(f"Upload failed: {e}")
            report["errors"].append(str(e))
            self._remove_from_s3()
        return report

    def _check_min_files(self):
        return len(os.listdir(self.staging_folder)) >= self.min_required_files

    def _check_s3_buckets_empty(self):
        for uri in self.s3_uris:
            bucket, prefix = self._split_s3_uri(uri)
            response = self.s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
            if "Contents" in response:
                return False
        return True

    def _upload_to_s3(self):
        count = 0
        for agid_folder in os.listdir(self.staging_folder):
            local_path = os.path.join(self.staging_folder, agid_folder)
            if not os.path.isdir(local_path):
                continue

            for s3_uri in self.s3_uris:
                bucket, prefix = self._split_s3_uri(s3_uri)
                s3_prefix = f"{prefix}/{agid_folder}"

                for file_name in os.listdir(local_path):
                    file_path = os.path.join(local_path, file_name)
                    s3_key = f"{s3_prefix}/{file_name}"
                    self.s3.upload_file(file_path, bucket, s3_key)
                    count += 1
        return count

    def _archive_staging_folder(self):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        zip_name = f"{os.path.basename(self.staging_folder)}_{timestamp}.zip"
        zip_path = os.path.join(self.archive_path, zip_name)

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(self.staging_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, self.staging_folder)
                    zipf.write(file_path, arcname)
        return zip_path

    def _cleanup_local_folder(self):
        for agid_folder in os.listdir(self.staging_folder):
            shutil.rmtree(os.path.join(self.staging_folder, agid_folder), ignore_errors=True)

    def _remove_from_s3(self):
        for s3_uri in self.s3_uris:
            bucket, prefix = self._split_s3_uri(s3_uri)
            response = self.s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
            if "Contents" in response:
                for obj in response["Contents"]:
                    self.s3.delete_object(Bucket=bucket, Key=obj["Key"])

    def _split_s3_uri(self, uri):
        if uri.startswith("s3://"):
            uri = uri[5:]
        parts = uri.split("/", 1)
        bucket = parts[0]
        prefix = parts[1] if len(parts) > 1 else ""
        return bucket, prefix
