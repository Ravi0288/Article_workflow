# Generated by Django 4.2 on 2024-02-22 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('actions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='archived_article_attribute',
            name='file_name_on_ftp',
            field=models.CharField(default='w', max_length=500),
            preserve_default=False,
        ),
    ]
