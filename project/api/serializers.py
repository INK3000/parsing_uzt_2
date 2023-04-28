from .models import CategoryOfJob, Job, TgUser
from rest_framework import serializers


class TgUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TgUser
        fields = ["id", "telegram_id", "subscriptions"]


class CategoryOfJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryOfJob
        fields = ["name", "event_target", "last_id"]


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            "date_upd",
            "name",
            "category",
            "company",
            "date_from",
            "date_to",
            "place",
            "url",
        ]
