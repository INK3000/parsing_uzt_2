# Generated by Django 4.2 on 2023-05-08 18:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0027_alter_category_last_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='job',
            old_name='name',
            new_name='title',
        ),
    ]