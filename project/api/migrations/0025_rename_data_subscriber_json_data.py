# Generated by Django 4.2 on 2023-05-05 12:32

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0024_rename_subscribed_to_subscriber_data"),
    ]

    operations = [
        migrations.RenameField(
            model_name="subscriber",
            old_name="data",
            new_name="json_data",
        ),
    ]