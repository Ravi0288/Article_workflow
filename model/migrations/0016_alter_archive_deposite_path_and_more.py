# Generated by Django 4.2 on 2024-10-02 07:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('model', '0015_alter_jsonified_articles_article_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='archive',
            name='deposite_path',
            field=models.TextField(default='/ai/metadata/ARCHIVE'),
        ),
        migrations.AlterField(
            model_name='article_attributes',
            name='deposite_path',
            field=models.TextField(default='/ai/metadata/ARTICLES'),
        ),
        migrations.AlterField(
            model_name='PROCESSED_ARTICLES',
            name='deposite_path',
            field=models.TextField(default='/ai/metadata/PROCESSED_ARTICLES'),
        ),
    ]
