from . import views
from django.urls import path

urlpatterns = [
    path("categories", views.CategoriesList.as_view()),
    path("jobs", views.JobList.as_view()),
    path("users", views.TgUserList.as_view()),
]
