from .s3_interaction import AlmaS3Uploader

staging_info = {
    "folder_path": "/data/metadata/marc_staging/new_publisher",
    "type": "new",
    "min_files": 10,
    "s3_uris": [
        "s3://alma-bucket-name/01NAL_INST/upload/12345678"
    ],
    "archive_path": "/data/metadata/archives",
    "active": True,
    "bucket_empty_check": True,
    "aws_access_key": "AKIAXXXXXX",
    "aws_secret_key": "XXXXXXXXXXX",
    "base_s3_uri": "s3://alma-bucket-name"
}

uploader = AlmaS3Uploader(staging_info)
report = uploader.run()
print(report)
