# Generated by Django 4.2 on 2023-05-23 15:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0006_token'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='token',
            name='key',
        ),
        migrations.AddField(
            model_name='token',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='token',
            name='token',
            field=models.CharField(default='GjmlyzQZtFGqtdKPDkEZ4yO9esrPz769-Fo7kiCTIVJjAZyK-sYneMzRrkvz4DyZG_g', max_length=50),
        ),
        migrations.AlterField(
            model_name='token',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
