# Generated by Django 4.2 on 2025-01-14 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('model', '0026_rename_article_attributes_article'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='provider_rec',
            field=models.TextField(blank=True, help_text='Provider article identifier', null=True),
        ),
    ]
