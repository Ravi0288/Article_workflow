# Generated by Django 4.2 on 2024-10-15 06:29

from django.db import migrations, models
import model.article


class Migration(migrations.Migration):

    dependencies = [
        ('model', '0021_article_attributes_is_content_changed_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Unreadable_files',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.TextField()),
                ('file_type', models.CharField(max_length=10)),
                ('file_content', models.FileField(help_text='Browse the file', storage=model.article.OverWriteStorage(), upload_to=model.article.get_invalid_file_path)),
                ('error_msg', models.TextField()),
                ('date_stamp', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.DeleteModel(
            name='Unreadable_xml_files',
        ),
    ]