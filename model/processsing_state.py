from django.db import models
class ProcessingState(models.Model):
    process_name = models.CharField(max_length=100, unique=True)
    in_progress = models.BooleanField(default=True)
    new_usda_record_processed = models.BigIntegerField(null=True)
    merge_usda_record_processed = models.BigIntegerField(null=True)
    new_publisher_record_processed = models.BigIntegerField(null=True)
    merge_publisher_record_processed = models.BigIntegerField(null=True)

