# Generated by Django 4.2 on 2023-05-14 19:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_subscription_user_and_category'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='subscription',
            name='user_and_category',
        ),
        migrations.AddConstraint(
            model_name='subscription',
            constraint=models.UniqueConstraint(fields=('category_id', 'subscriber_id'), name='user_and_category'),
        ),
    ]
