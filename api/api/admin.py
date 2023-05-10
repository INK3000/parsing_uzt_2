from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from . import models


class JobAdmin(admin.ModelAdmin):
    list_display = ["id", "link_title",
                    "company_short", "category", "link_out"]
    list_filter = ["category"]
    search_fields = ["place", "title", "company"]

    def company_short(self, obj):
        ...
        short_title = obj.company[:31]
        ending = "..." if len(obj.company) > 30 else ""
        return format_html(
            '<span title="{}">{}{}</span>', obj.company, short_title, ending
        )

    company_short.short_description = "Company"

    def link_title(self, obj):
        caption = obj.title
        link_to_obj = reverse("admin:api_job_change", args=[obj.pk])
        return format_html('<a href="{}" target="_self">{}<a>', link_to_obj, caption)

    link_title.short_description = "Title"

    def link_out(self, obj):
        caption = "Go to..."
        link_to_job = obj.url
        return format_html('<a href="{}" target="_blank">{}<a>', link_to_job, caption)

    link_out.short_description = "Url"


class SubscriberAdmin(admin.ModelAdmin):
    list_display = ["telegram_id", "date_created"]
    fields = ["telegram_id", "subscriptions", "date_created"]
    readonly_fields = ["telegram_id", "date_created", "subscriptions"]
    # filter_horizontal = ["subscriptions"]


admin.site.register(models.Subscriber, SubscriberAdmin)
admin.site.register(models.Job, JobAdmin)
admin.site.register(models.Category)
