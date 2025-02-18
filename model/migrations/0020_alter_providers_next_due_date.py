# Generated by Django 4.2 on 2024-10-12 06:34

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('model', '0019_remove_provider_meta_data_deposit_destination_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='providers',
            name='next_due_date',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='This will be filled. In case you need to set due date manually, set last_error_message = manual and than set this field'),
        ),
    ]
