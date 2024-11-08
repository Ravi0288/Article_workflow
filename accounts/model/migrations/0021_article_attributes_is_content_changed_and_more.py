# Generated by Django 4.2 on 2024-10-13 07:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('model', '0020_alter_providers_next_due_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='article_attributes',
            name='is_content_changed',
            field=models.BooleanField(default=False, help_text='Flag to maintain if the existing content is changed and file_content is updated'),
        ),
        migrations.AlterField(
            model_name='archive',
            name='is_content_changed',
            field=models.BooleanField(default=False, help_text='Flag to maintain if the existing content is changed and file_content is updated'),
        ),
    ]
