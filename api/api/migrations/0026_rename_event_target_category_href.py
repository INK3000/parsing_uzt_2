# Generated by Django 4.2 on 2023-05-08 09:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0025_rename_data_subscriber_json_data'),
    ]

    operations = [
        migrations.RenameField(
            model_name='category',
            old_name='event_target',
            new_name='href',
        ),
    ]