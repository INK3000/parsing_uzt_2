from .models import CategoryOfJob, Job, TgUser
from django.contrib import admin

admin.site.register(TgUser)
admin.site.register(Job)
admin.site.register(CategoryOfJob)
