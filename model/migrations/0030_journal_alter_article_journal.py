# Generated by Django 4.2 on 2025-02-05 04:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('model', '0029_alter_article_citation_pickle'),
    ]

    operations = [
        migrations.CreateModel(
            name='Journal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('journal_title', models.CharField(max_length=150)),
                ('publisher', models.CharField(max_length=256)),
                ('issn', models.CharField(max_length=24)),
                ('collection_status', models.CharField(choices=[('pending', 'pending'), ('accepted', 'accepted'), ('from_submission', 'from_submission'), ('rejected', 'rejected')], max_length=16)),
                ('harvest_source', models.CharField(max_length=128)),
                ('local_id', models.CharField(max_length=64)),
                ('mmsid', models.CharField(max_length=64)),
                ('last_updated', models.CharField(default='', max_length=8)),
                ('note', models.CharField(default='', max_length=256)),
            ],
        ),
        migrations.AlterField(
            model_name='article',
            name='journal',
            field=models.ForeignKey(help_text='This field value will assigned automatically with the value assigned in article_file', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='article_journal', to='model.journal'),
        ),
    ]
