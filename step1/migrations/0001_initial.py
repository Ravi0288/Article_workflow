# Generated by Django 4.2 on 2024-03-25 12:28

from django.db import migrations, models
import django.db.models.deletion
import step1.archive_article
import configurations.common


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Email_notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('applicable_to', models.CharField(blank=True, max_length=50, null=True)),
                ('email_from', models.TextField()),
                ('email_to', models.TextField()),
                ('email_subject', models.TextField(default='Error Occured')),
                ('email_body', models.TextField(default='Error Occured')),
            ],
        ),
        migrations.CreateModel(
            name='Provider_model',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('official_name', models.CharField(max_length=100)),
                ('working_name', models.CharField(max_length=50)),
                ('in_production', models.BooleanField(max_length=15)),
                ('archive_switch', models.BooleanField(max_length=15)),
                ('article_switch', models.BooleanField(max_length=15)),
                ('requirement_override', models.BooleanField(max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='Provider_meta_data_FTP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('server', models.TextField()),
                ('protocol', models.CharField(max_length=10)),
                ('site_path', models.CharField(max_length=50)),
                ('account', models.CharField(max_length=50)),
                ('password', configurations.common.EncryptedField(blank=True, null=True)),
                ('minimum_delivery_fq', models.IntegerField()),
                ('last_pull_time', models.DateTimeField(auto_now=True)),
                ('pull_switch', models.BooleanField()),
                ('last_pull_status', models.CharField(default='success', max_length=10)),
                ('last_error_message', models.TextField(blank=True, null=True)),
                ('next_due_date', models.DateTimeField(null=True)),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ftp_provider', to='step1.provider_model')),
            ],
        ),
        migrations.CreateModel(
            name='Provider_meta_data_API',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_meta_type', models.CharField(blank=True, choices=[('Chorus', 'Chorus'), ('CrossRef', 'CrossRef'), ('Submission', 'Submission')], max_length=20, null=True)),
                ('base_url', models.URLField()),
                ('identifier_code', models.CharField(max_length=50)),
                ('identifier_type', models.CharField(max_length=50)),
                ('last_pull_time', models.DateTimeField(auto_now=True)),
                ('api_switch', models.BooleanField()),
                ('is_token_required', models.BooleanField(default=False)),
                ('site_token', configurations.common.EncryptedField(blank=True, null=True)),
                ('minimum_delivery_fq', models.IntegerField()),
                ('last_pull_status', models.CharField(default='success', max_length=10)),
                ('last_error_message', models.TextField(blank=True, null=True)),
                ('next_due_date', models.DateTimeField(null=True)),
                ('proxy_host_url', models.TextField(null=True)),
                ('external_library_url', models.TextField(null=True)),
                ('is_paginated', models.BooleanField(default=False)),
                ('page_number', models.IntegerField(null=True)),
                ('last_accessed_page', models.IntegerField(null=True)),
                ('email_notification', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='step1.email_notification')),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='api_provider', to='step1.provider_model')),
            ],
        ),
        migrations.CreateModel(
            name='Fetch_history',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(default='success', max_length=10)),
                ('error_message', models.TextField(blank=True, null=True)),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='fetch_history', to='step1.provider_model')),
            ],
        ),
        migrations.CreateModel(
            name='Email_history',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(default='success', max_length=10)),
                ('email_subject', models.TextField(default='Error Occured')),
                ('email_body', models.TextField(default='Error Occured')),
                ('email_ref', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='email_notification', to='step1.email_notification')),
            ],
        ),
        migrations.CreateModel(
            name='Archived_article_attribute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_content', models.FileField(blank=True, null=True, storage=step1.archive_article.OverWriteStorage(), upload_to=step1.archive_article.get_file_path)),
                ('file_name_on_source', models.CharField(max_length=500)),
                ('file_size', models.BigIntegerField(default=0)),
                ('file_type', models.CharField(max_length=20)),
                ('unzipped_folder_size', models.BigIntegerField(default=0)),
                ('received_on', models.DateTimeField(auto_now_add=True)),
                ('processed_on', models.DateTimeField(null=True)),
                ('status', models.CharField(choices=[('success', 'success'), ('waiting', 'waiting'), ('processed', 'processed'), ('failed', 'failed')], max_length=12)),
                ('notes', models.TextField(default='N/A')),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='archives', to='step1.provider_model')),
            ],
        ),
    ]
