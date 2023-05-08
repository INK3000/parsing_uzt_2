# Generated by Django 4.2 on 2023-05-05 11:35

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0021_alter_category_options"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="subscriber",
            options={"ordering": ["-date_created"]},
        ),
        migrations.RemoveField(
            model_name="subscriber",
            name="id",
        ),
        migrations.AddField(
            model_name="subscriber",
            name="date_created",
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name="subscriber",
            name="telegram_id",
            field=models.PositiveIntegerField(primary_key=True, serialize=False),
        ),
    ]