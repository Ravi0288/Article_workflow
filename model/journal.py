from django.db import models

COLLECTION_STATUSES= (
    ('pending', 'pending'),
    ('accepted','accepted'),
    ('from_submission', 'from_submission'),
    ('rejected', 'rejected')
)

class Journal(models.Model):
    journal_title = models.CharField(max_length=150, null=True, blank=True, help_text="Journal Title")
    publisher = models.CharField(max_length=256, null=True, blank=True, help_text="Publisher Code" )
    issn = models.CharField(max_length=24, null=True, blank=True, help_text="ISSN Number")
    collection_status = models.CharField(max_length=16, choices=COLLECTION_STATUSES, help_text="Select available collection status from the drop down")
    harvest_source = models.CharField(max_length=128, null=True, blank=True, help_text="Harvest Source")
    local_id = models.CharField(max_length=64, null=True, blank=True, help_text="Local ID")
    mmsid = models.CharField(max_length=64, null=True, blank=True, help_text="Local ID")
    last_updated = models.DateTimeField(auto_now=True)
    note = models.CharField(max_length=256, null=True, blank=True, help_text="Any error msg or important msg to be assigned")