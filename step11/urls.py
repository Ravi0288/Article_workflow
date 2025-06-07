from django.urls import path, include
from .migrate_to_step_11 import migrate_to_step11
from .empty_s3 import empty_s3_bucket



urlpatterns = [
    path('migrate-to-step-11/', migrate_to_step11, name="migrate-to-step-11"),
    path('empty-s3-bucket/', empty_s3_bucket, name="empty-s3-bucket"),
]