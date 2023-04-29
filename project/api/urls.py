from django.urls import path

from . import views

urlpatterns = [
    path("categories", views.CategoriesList.as_view()),
    path("categories/<int:pk>", views.CategoryRetrieveUpdate.as_view()),
    path("jobs", views.JobCreate.as_view()),
    path("jobs/<int:category>", views.JobListByCategory.as_view()),
    path("users", views.TgUserList.as_view()),
    path("users/<int:telegram_id>", views.TgUserDetail.as_view()),
]
