# Generated by Django 4.2 on 2024-10-11 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_authorization_menu'),
    ]

    operations = [
        migrations.AlterField(
            model_name='authorization',
            name='menu',
            field=models.CharField(choices=[('provider-detail', 'provider-detail'), ('fetch-history-detail', 'fetch-history-detail'), ('archive-article-list', 'archive-article-list'), ('provider-list', 'provider-list'), ('download-from-ftp', 'download-from-ftp'), ('login', 'login'), ('archive-article-detail', 'archive-article-detail'), ('provider-ftp-list', 'provider-ftp-list'), ('download-from-crossref-api', 'download-from-crossref-api'), ('unreadable-xml-files-detail', 'unreadable-xml-files-detail'), ('fetch-history-list', 'fetch-history-list'), ('provider-api-detail', 'provider-api-detail'), ('unreadable-xml-files-list', 'unreadable-xml-files-list'), ('action-deposites', 'action-deposites'), ('articles-list', 'articles-list'), ('provider-ftp-detail', 'provider-ftp-detail'), ('api-root', 'api-root'), ('articles-detail', 'articles-detail'), ('migrate-to-step-2', 'migrate-to-step-2'), ('download-from-chorus-api', 'download-from-chorus-api'), ('provider-api-list', 'provider-api-list'), ('logout', 'logout'), ('download-from-sftp', 'download-from-sftp'), ('provider-deposite-list', 'provider-deposite-list'), ('provider-deposite-detail', 'provider-deposite-detail'), ('download-from-submission-api', 'download-from-submission-api')], max_length=100),
        ),
    ]
