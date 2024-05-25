# Generated by Django 4.2 on 2024-05-25 04:46

import configurations.common
from django.db import migrations, models
import django.db.models.deletion
import model.archive
import model.article


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Archive',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_content', models.FileField(blank=True, help_text='Browse the file', null=True, storage=model.archive.OverWriteStorage(), upload_to=model.archive.get_file_path)),
                ('file_name_on_source', models.CharField(blank=True, help_text='File name will be assigned automatically of received file', max_length=500, null=True)),
                ('file_name_on_local_storage', models.CharField(blank=True, help_text='File name will be assigned automatically as id.extesion', max_length=500, null=True)),
                ('file_size', models.IntegerField(default=0, help_text='File size will be assigned automatically')),
                ('file_type', models.CharField(help_text='File type will be assigned automatically', max_length=20)),
                ('unique_key', models.CharField(blank=True, help_text='Unique key to identify this record uniquely. Indentifier code or DOI etc', max_length=500, null=True)),
                ('received_on', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('success', 'success'), ('waiting', 'waiting'), ('processed', 'processed'), ('failed', 'failed')], help_text='Last access status', max_length=12)),
                ('is_processed', models.BooleanField(default=False, help_text='Flag to maintain if the record is processed for step 2')),
                ('processed_on', models.DateTimeField(null=True)),
                ('is_content_changed', models.BooleanField(default=False, help_text='Flag to maintain if the existing content is changed and file_content is update')),
            ],
        ),
        migrations.CreateModel(
            name='Providers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('official_name', models.CharField(max_length=64)),
                ('working_name', models.CharField(max_length=64)),
                ('in_production', models.BooleanField(default=True)),
                ('provider_type', models.CharField(choices=[('FTP', 'FTP'), ('API', 'API')], default='FTP', max_length=4)),
            ],
        ),
        migrations.CreateModel(
            name='Unreadable_xml_files',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_name', models.CharField(max_length=100)),
                ('error_msg', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Provider_meta_data_FTP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('server', models.TextField(help_text='Enter FTP address')),
                ('protocol', models.CharField(choices=[('FTP', 'FTP'), ('SFTP', 'SFTP')], help_text='Enter Protocol used by this FTP. i.e. FTP / SFTP', max_length=10)),
                ('site_path', models.TextField(default='/', help_text='Enter default location where file is stored on FTP server')),
                ('is_password_required', models.BooleanField(default=True, help_text='Is this FTP password protected?')),
                ('account', models.CharField(blank=True, help_text='Username to login to FTP. if is_password_required is selected this field is required', max_length=100, null=True)),
                ('password', configurations.common.EncryptedField(blank=True, help_text='Password to login to FTP. if is_password_required is selected this field is required', null=True)),
                ('minimum_delivery_fq', models.IntegerField(help_text='Enter frequency (number of days) when to sync the data with FTP')),
                ('next_due_date', models.DateTimeField(help_text="This will be filled automatically base on minimum_delivery_frequency. Don't enter anything here", null=True)),
                ('last_pull_time', models.DateTimeField(auto_now=True, help_text='This will be auto field as and when the FTP will be accessed')),
                ('last_pull_status', models.CharField(default='success', help_text="For the first time enter 'Initial'. This field will maintain last sync status success or failed", max_length=10)),
                ('last_error_message', models.TextField(blank=True, help_text="In case of error last error message will be stored here. Don't enter anything here", null=True)),
                ('provider', models.ForeignKey(help_text='Select Provider name', on_delete=django.db.models.deletion.DO_NOTHING, related_name='ftp_provider', to='model.providers')),
            ],
        ),
        migrations.CreateModel(
            name='Provider_meta_data_API',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_meta_type', models.CharField(blank=True, choices=[('Chorus', 'Chorus'), ('CrossRef', 'CrossRef'), ('Submission', 'Submission')], help_text='Select Type of API', max_length=20, null=True)),
                ('base_url', models.URLField(help_text='Enter Base URL of the API')),
                ('identifier_type', models.CharField(help_text="Enter Identifier type / name. For example 'usda funder id' ", max_length=50)),
                ('identifier_code', models.CharField(help_text='Enter Identifier code for example 100000199', max_length=50)),
                ('is_token_required', models.BooleanField(default=False, help_text='If this API endpoint is password protected select the check box')),
                ('site_token', configurations.common.EncryptedField(blank=True, help_text="If 'is_token_required' is selected provide password / token for API", null=True)),
                ('minimum_delivery_fq', models.IntegerField(help_text='Enter frequency (number of days) when to sync the data with API')),
                ('next_due_date', models.DateTimeField(help_text="This will be filled automatically base on minimum_delivery_frequency. Don't enter anything here", null=True)),
                ('last_pull_time', models.DateTimeField(auto_now=True, help_text='This will be auto field as and when the api will be accessed')),
                ('last_pull_status', models.CharField(default='success', help_text="For the first time enter 'Initial'. This field will maintain last sync status success or failed", max_length=10)),
                ('last_error_message', models.TextField(blank=True, help_text="In case of error last error message will be stored here. Don't enter anything here", null=True)),
                ('proxy_host_url', models.TextField(blank=True, help_text='Provide proxy hosts if any. This is optional', null=True)),
                ('external_library_url', models.TextField(blank=True, help_text='Provide external library address if any. This is optional', null=True)),
                ('is_paginated', models.BooleanField(default=False, help_text='Is this api paginated? Select if yes. This is optional')),
                ('page_number', models.IntegerField(default=1, help_text='If paginated, enter the first page number. Default is 1', null=True)),
                ('provider', models.ForeignKey(help_text='Select Provider name', on_delete=django.db.models.deletion.DO_NOTHING, related_name='api_provider', to='model.providers')),
            ],
        ),
        migrations.CreateModel(
            name='Fetch_history',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(default='success', max_length=10)),
                ('error_message', models.TextField(blank=True, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='fetch_history', to='model.providers')),
            ],
        ),
        migrations.CreateModel(
            name='Article_attributes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('article_file', models.FileField(help_text='Browse the file', storage=model.article.OverWriteStorage(), upload_to=model.article.get_file_path)),
                ('title', models.TextField(blank=True, help_text='Article title', null=True)),
                ('type_of_record', models.CharField(choices=[('article', 'article'), ('retraction', 'retraction'), ('letter to the editor', 'letter to the editor')], help_text='Select from drop down', max_length=24)),
                ('last_stage', models.IntegerField(default=2, help_text='Last stage article passed through 1-11')),
                ('last_status', models.CharField(choices=[('active', 'active'), ('failed', 'failed'), ('completed', 'completed')], default='active', help_text='Select from drop down', max_length=10)),
                ('note', models.TextField(default='ok', help_text='Note, warning or error note')),
                ('DOI', models.TextField(blank=True, help_text='A unique and persistent identifier', null=True)),
                ('PID', models.TextField(blank=True, help_text='A locally assign identifie', null=True)),
                ('MMSID', models.TextField(blank=True, help_text="The article's Alma identifer", null=True)),
                ('provider_rec', models.CharField(blank=True, help_text='Provider article identifier', max_length=10, null=True)),
                ('start_date', models.DateTimeField(auto_now=True, help_text='The date the article object was created')),
                ('current_date', models.DateTimeField(auto_now_add=True, help_text='The date finished the last stage')),
                ('end_date', models.DateTimeField(help_text='The data the article is staged for Alma', null=True)),
                ('archive', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='archives', to='model.archive')),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='provsider', to='model.providers')),
            ],
        ),
        migrations.AddField(
            model_name='archive',
            name='provider',
            field=models.ForeignKey(help_text='Select provider', on_delete=django.db.models.deletion.DO_NOTHING, related_name='archives', to='model.providers'),
        ),
    ]
