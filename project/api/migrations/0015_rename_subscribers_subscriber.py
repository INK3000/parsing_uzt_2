# Generated by Django 4.2 on 2023-05-03 13:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_rename_categoryofjob_category_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Subscribers',
            new_name='Subscriber',
        ),
    ]
