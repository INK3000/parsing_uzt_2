from django.contrib import admin

from .models import Category, Job, Subscribers


class JobAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "company", "category"]


admin.site.register(Subscribers)
admin.site.register(Job, JobAdmin)
admin.site.register(Category)
