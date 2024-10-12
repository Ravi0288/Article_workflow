# Generated by Django 4.2 on 2024-10-12 04:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_authorization_menu'),
    ]

    operations = [
        migrations.AlterField(
            model_name='authorization',
            name='menu',
            field=models.CharField(choices=[('articles-list', 'articles-list'), ('unreadable-xml-files-detail', 'unreadable-xml-files-detail'), ('fetch-history-list', 'fetch-history-list'), ('unreadable-xml-files-list', 'unreadable-xml-files-list'), ('download-from-sftp', 'download-from-sftp'), ('provider-ftp-detail', 'provider-ftp-detail'), ('provider-list', 'provider-list'), ('download-from-ftp', 'download-from-ftp'), ('action-deposites', 'action-deposites'), ('provider-api-detail', 'provider-api-detail'), ('logout', 'logout'), ('login', 'login'), ('api-root', 'api-root'), ('provider-ftp-list', 'provider-ftp-list'), ('archive-article-list', 'archive-article-list'), ('fetch-history-detail', 'fetch-history-detail'), ('download-from-chorus-api', 'download-from-chorus-api'), ('archive-article-detail', 'archive-article-detail'), ('provider-deposite-detail', 'provider-deposite-detail'), ('download-from-crossref-api', 'download-from-crossref-api'), ('migrate-to-step2', 'migrate-to-step2'), ('download-from-submission-api', 'download-from-submission-api'), ('provider-detail', 'provider-detail'), ('provider-api-list', 'provider-api-list'), ('provider-deposite-list', 'provider-deposite-list'), ('articles-detail', 'articles-detail')], max_length=100),
        ),
    ]
