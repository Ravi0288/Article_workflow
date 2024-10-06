# Generated by Django 4.2 on 2024-10-02 07:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='authorization',
            name='menu',
            field=models.CharField(choices=[('unreadable-xml-files-detail', 'unreadable-xml-files-detail'), ('provider-detail', 'provider-detail'), ('provider-api-detail', 'provider-api-detail'), ('provider-list', 'provider-list'), ('download-from-ftp', 'download-from-ftp'), ('migrate-to-step2', 'migrate-to-step2'), ('articles-detail', 'articles-detail'), ('provider-api-list', 'provider-api-list'), ('login', 'login'), ('archive-article-detail', 'archive-article-detail'), ('download-from-chorus-api', 'download-from-chorus-api'), ('provider-ftp-detail', 'provider-ftp-detail'), ('archive-article-list', 'archive-article-list'), ('articles-list', 'articles-list'), ('api-root', 'api-root'), ('provider-ftp-list', 'provider-ftp-list'), ('download-from-submission-api', 'download-from-submission-api'), ('download-from-crossref-api', 'download-from-crossref-api'), ('logout', 'logout'), ('fetch-history-list', 'fetch-history-list'), ('unreadable-xml-files-list', 'unreadable-xml-files-list'), ('fetch-history-detail', 'fetch-history-detail')], max_length=100),
        ),
    ]