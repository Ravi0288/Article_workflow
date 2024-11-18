from django.db import models


class Provider_access_report(models.Model):
    id = models.AutoField(primary_key=True)
    provider = models.CharField(blank=True, null=True, max_length=50) 
    acronym = models.CharField(blank=True, null=True, max_length=50)
    frequency = models.IntegerField()
    overdue_in_days = models.CharField(max_length=15)
    date1 = models.DateField()
    date2 = models.DateField()
    date3 = models.DateField()
    date4 = models.DateField()
    date5 = models.DateField()
    date6 = models.DateField()

    class Meta:
        managed = False
        db_table = 'Provider_access_report'


class Provider_backlog_report(models.Model):
    id = models.AutoField(primary_key=True)
    provider = models.CharField(blank=True, null=True, max_length=50) 
    acronym = models.CharField(blank=True, null=True, max_length=50)
    overdue_in_days = models.CharField(max_length=15)
    archive_in_backlog = models.IntegerField()
    articles_waiting = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'Provider_backlog_report'




