from django.db import models

class SchedulerLog(models.Model):
    step = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=(
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed')
    ))
    error_message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.job_name} - {self.status} at {self.start_time}"
