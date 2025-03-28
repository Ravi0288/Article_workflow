# Generated by Django 4.2 on 2024-10-12 04:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_alter_authorization_menu'),
    ]

    operations = [
        migrations.AlterField(
            model_name='authorization',
            name='menu',
            field=models.CharField(choices=[('fetch-history-detail', 'fetch-history-detail'), ('unreadable-xml-files-detail', 'unreadable-xml-files-detail'), ('articles-detail', 'articles-detail'), ('archive-article-list', 'archive-article-list'), ('download-from-sftp', 'download-from-sftp'), ('provider-ftp-list', 'provider-ftp-list'), ('api-root', 'api-root'), ('archive-article-detail', 'archive-article-detail'), ('provider-api-list', 'provider-api-list'), ('provider-deposite-list', 'provider-deposite-list'), ('action-deposites', 'action-deposites'), ('fetch-history-list', 'fetch-history-list'), ('download-from-chorus-api', 'download-from-chorus-api'), ('provider-list', 'provider-list'), ('download-from-crossref-api', 'download-from-crossref-api'), ('migrate-to-step-2', 'migrate-to-step-2'), ('download-from-ftp', 'download-from-ftp'), ('unreadable-xml-files-list', 'unreadable-xml-files-list'), ('login', 'login'), ('articles-list', 'articles-list'), ('provider-ftp-detail', 'provider-ftp-detail'), ('provider-api-detail', 'provider-api-detail'), ('download-from-submission-api', 'download-from-submission-api'), ('provider-deposite-detail', 'provider-deposite-detail'), ('logout', 'logout'), ('provider-detail', 'provider-detail')], max_length=100),
        ),
    ]
