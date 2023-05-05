from django.contrib import admin

from . import models


class JobAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "company", "category"]


class SubscriberAdmin(admin.ModelAdmin):
    list_display = ["telegram_id", "date_created"]
    readonly_fields = ["date_created"]


admin.site.register(models.Subscriber, SubscriberAdmin)
admin.site.register(models.Job, JobAdmin)
admin.site.register(models.Category)
