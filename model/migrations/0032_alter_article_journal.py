# Generated by Django 4.2 on 2025-02-10 16:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('model', '0031_alter_journal_collection_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='journal',
            field=models.ForeignKey(default=None, help_text='This field value will assigned automatically with the value assigned in article_file', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='article_journal', to='model.journal'),
        ),
    ]
