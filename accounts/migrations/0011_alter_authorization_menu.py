# Generated by Django 4.2 on 2024-11-27 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_alter_authorization_menu'),
    ]

    operations = [
        migrations.AlterField(
            model_name='authorization',
            name='menu',
            field=models.CharField(choices=[('provider-api-list', 'provider-api-list'), ('login', 'login'), ('download-from-ftp', 'download-from-ftp'), ('provider-deposite-list', 'provider-deposite-list'), ('articles-detail', 'articles-detail'), ('articles-list', 'articles-list'), ('action-deposites', 'action-deposites'), ('provider-list', 'provider-list'), ('provider-deposite-detail', 'provider-deposite-detail'), ('provider-api-detail', 'provider-api-detail'), ('download-from-sftp', 'download-from-sftp'), ('download-from-submission-api', 'download-from-submission-api'), ('migrate-to-step-2', 'migrate-to-step-2'), ('unreadable-files-detail', 'unreadable-files-detail'), ('unreadable-files-list', 'unreadable-files-list'), ('archive-article-list', 'archive-article-list'), ('archive-article-detail', 'archive-article-detail'), ('provider-ftp-detail', 'provider-ftp-detail'), ('provider-ftp-list', 'provider-ftp-list'), ('provider-detail', 'provider-detail'), ('fetch-history-detail', 'fetch-history-detail'), ('fetch-history-list', 'fetch-history-list'), ('logout', 'logout'), ('api-root', 'api-root'), ('download-from-crossref-api', 'download-from-crossref-api'), ('download-from-chorus-api', 'download-from-chorus-api')], max_length=100),
        ),
    ]
