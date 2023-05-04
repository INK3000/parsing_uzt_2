from django.contrib import admin

from . import models


class JobAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "company", "category"]


admin.site.register(models.Subscriber)
admin.site.register(models.Job, JobAdmin)
admin.site.register(models.Category)
