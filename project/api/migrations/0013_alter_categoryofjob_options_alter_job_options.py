# Generated by Django 4.2 on 2023-05-02 14:27

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0012_alter_job_options"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="categoryofjob",
            options={"ordering": ["id"], "verbose_name": "Category"},
        ),
        migrations.AlterModelOptions(
            name="job",
            options={"ordering": ["-id"]},
        ),
    ]
