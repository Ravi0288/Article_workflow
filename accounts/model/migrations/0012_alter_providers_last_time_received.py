# Generated by Django 4.2 on 2024-08-15 01:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('model', '0011_alter_article_attributes_pid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='providers',
            name='last_time_received',
            field=models.DateTimeField(help_text='This will be auto field as and when the FTP will be accessed'),
        ),
    ]
