# Generated by Django 4.2 on 2023-05-02 13:24

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0011_alter_job_unique_together_job_category_url"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="job",
            options={"ordering": ["-id"], "verbose_name": "Category"},
        ),
    ]
