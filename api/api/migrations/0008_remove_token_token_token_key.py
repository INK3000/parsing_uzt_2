# Generated by Django 4.2 on 2023-05-23 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_remove_token_key_token_created_at_token_token_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='token',
            name='token',
        ),
        migrations.AddField(
            model_name='token',
            name='key',
            field=models.CharField(default='koDfs76pOHAZg9a5-9ECaaLs3TtINe8SElVZsjywdZkw-eYEnGKxiluAX_1YU3mM-ok', max_length=67),
        ),
    ]
