# Generated by Django 4.2 on 2024-11-27 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Provider_access_report',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('provider', models.CharField(blank=True, max_length=50, null=True)),
                ('acronym', models.CharField(blank=True, max_length=50, null=True)),
                ('frequency', models.IntegerField()),
                ('overdue_in_days', models.CharField(max_length=15)),
                ('date1', models.DateField()),
                ('date2', models.DateField()),
                ('date3', models.DateField()),
                ('date4', models.DateField()),
                ('date5', models.DateField()),
                ('date6', models.DateField()),
            ],
            options={
                'db_table': 'Provider_access_report',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Provider_backlog_report',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('provider', models.CharField(blank=True, max_length=50, null=True)),
                ('acronym', models.CharField(blank=True, max_length=50, null=True)),
                ('overdue_in_days', models.CharField(max_length=15)),
                ('archive_in_backlog', models.IntegerField()),
                ('articles_waiting', models.IntegerField()),
            ],
            options={
                'db_table': 'Provider_backlog_report',
                'managed': False,
            },
        ),
    ]