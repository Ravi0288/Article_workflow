# Generated by Django 4.2 on 2024-10-02 07:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_authorization_menu'),
    ]

    operations = [
        migrations.AlterField(
            model_name='authorization',
            name='menu',
            field=models.CharField(choices=[('provider-list', 'provider-list'), ('download-from-submission-api', 'download-from-submission-api'), ('articles-list', 'articles-list'), ('archive-article-detail', 'archive-article-detail'), ('migrate-to-step2', 'migrate-to-step2'), ('unreadable-xml-files-list', 'unreadable-xml-files-list'), ('fetch-history-detail', 'fetch-history-detail'), ('download-from-ftp', 'download-from-ftp'), ('archive-article-list', 'archive-article-list'), ('download-from-crossref-api', 'download-from-crossref-api'), ('provider-api-list', 'provider-api-list'), ('provider-ftp-list', 'provider-ftp-list'), ('api-root', 'api-root'), ('provider-ftp-detail', 'provider-ftp-detail'), ('unreadable-xml-files-detail', 'unreadable-xml-files-detail'), ('download-from-chorus-api', 'download-from-chorus-api'), ('login', 'login'), ('fetch-history-list', 'fetch-history-list'), ('logout', 'logout'), ('provider-api-detail', 'provider-api-detail'), ('provider-detail', 'provider-detail'), ('articles-detail', 'articles-detail')], max_length=100),
        ),
    ]
