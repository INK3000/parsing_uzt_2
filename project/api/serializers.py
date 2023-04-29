from rest_framework import serializers

from .models import CategoryOfJob, Job, TgUser

# Telegram users


class TgUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TgUser
        fields = ["id", "telegram_id", "subscriptions"]


# Category of jobs


class CategoryOfJobCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryOfJob
        fields = ["id", "name", "event_target", "last_id"]


class CategoryOfJobUpdateSerializer(serializers.ModelSerializer):
    class Meta(CategoryOfJobCreateSerializer.Meta):
        read_only_fields = ["id", "name", "event_target"]


# Jobs


class JobCreateSerializer(serializers.ModelSerializer):
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
