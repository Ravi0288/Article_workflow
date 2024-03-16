# Generated by Django 4.2 on 2024-03-16 06:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('actions', '0014_provider_meta_data_api_is_paginated_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='provider_meta_data_api',
            name='is_token_required',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='provider_meta_data_api',
            name='site_token',
            field=models.TextField(blank=True, null=True),
        ),
    ]
