# Generated by Django 4.2 on 2025-01-10 10:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('model', '0023_article_rename_deposite_path_archive_deposit_path_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article_attributes',
            name='deposit_path',
        ),
        migrations.AddField(
            model_name='providers',
            name='source_schema_acronym',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='providers',
            name='delivery_method',
            field=models.CharField(blank=True, choices=[('Deposit', 'Deposit'), ('FTP', 'FTP'), ('SFTP', 'SFTP'), ('API', 'API')], max_length=50, null=True),
        ),
    ]
