from django.db import models


class Provider_access_report(models.Model):
    id = models.AutoField(primary_key=True)
    provider = models.CharField(blank=True, null=True, max_length=50) 
    acronym = models.CharField(blank=True, null=True, max_length=50)
    frequency = models.BigIntegerField()
    overdue_in_days = models.IntegerField()
    date1 = models.DateTimeField()
    date2 = models.DateTimeField()
    date3 = models.DateTimeField()
    date4 = models.DateTimeField()
    date5 = models.DateTimeField()
    date6 = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'Provider_access_report'


class Provider_delivery_report(models.Model):
    id = models.AutoField(primary_key=True)
    provider = models.CharField(blank=True, null=True, max_length=50) 
    acronym = models.CharField(blank=True, null=True, max_length=50)
    overdue_in_days = models.IntegerField()
    archive_in_backlog = models.BigIntegerField()
    articles_waiting = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'Provider_delivery_report'




