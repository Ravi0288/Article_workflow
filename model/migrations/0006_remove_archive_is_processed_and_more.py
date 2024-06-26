# Generated by Django 4.2 on 2024-06-28 15:59

from django.db import migrations, models
import pathlib


class Migration(migrations.Migration):

    dependencies = [
        ('model', '0005_provider_meta_data_api_pull_switch_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='archive',
            name='is_processed',
        ),
        migrations.RemoveField(
            model_name='provider_meta_data_api',
            name='last_error_message',
        ),
        migrations.RemoveField(
            model_name='provider_meta_data_api',
            name='last_pull_status',
        ),
        migrations.RemoveField(
            model_name='provider_meta_data_api',
            name='last_pull_time',
        ),
        migrations.RemoveField(
            model_name='provider_meta_data_api',
            name='minimum_delivery_fq',
        ),
        migrations.RemoveField(
            model_name='provider_meta_data_api',
            name='next_due_date',
        ),
        migrations.RemoveField(
            model_name='provider_meta_data_ftp',
            name='last_error_message',
        ),
        migrations.RemoveField(
            model_name='provider_meta_data_ftp',
            name='last_pull_status',
        ),
        migrations.RemoveField(
            model_name='provider_meta_data_ftp',
            name='last_pull_time',
        ),
        migrations.RemoveField(
            model_name='provider_meta_data_ftp',
            name='minimum_delivery_fq',
        ),
        migrations.RemoveField(
            model_name='provider_meta_data_ftp',
            name='next_due_date',
        ),
        migrations.AddField(
            model_name='archive',
            name='deposite_path',
            field=models.TextField(default=pathlib.PureWindowsPath('E:/NAL-USDA/NAL_LIBRARY_SYSTEM/ARCHIVE')),
        ),
        migrations.AddField(
            model_name='article_attributes',
            name='deposite_path',
            field=models.TextField(default=pathlib.PureWindowsPath('E:/NAL-USDA/NAL_LIBRARY_SYSTEM/ARCHIVE')),
        ),
        migrations.AddField(
            model_name='providers',
            name='last_error_message',
            field=models.TextField(blank=True, help_text="In case of error last error message will be stored here. Don't enter anything here", null=True),
        ),
        migrations.AddField(
            model_name='providers',
            name='last_time_received',
            field=models.DateTimeField(auto_now=True, help_text='This will be auto field as and when the FTP will be accessed'),
        ),
        migrations.AddField(
            model_name='providers',
            name='minimum_delivery_fq',
            field=models.IntegerField(default=30, help_text='Enter frequency (number of days) when to sync the data with API'),
        ),
        migrations.AddField(
            model_name='providers',
            name='next_due_date',
            field=models.DateTimeField(help_text="This will be filled automatically base on minimum_delivery_frequency. Don't enter anything here", null=True),
        ),
        migrations.AddField(
            model_name='providers',
            name='status',
            field=models.CharField(default='success', help_text="For the first time enter 'Initial'. This field will maintain last sync status success or failed", max_length=10),
        ),
    ]
