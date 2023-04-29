import pprint

from django.contrib.admin.utils import lookup_field
from rest_framework import generics

from .models import CategoryOfJob, Job, TgUser
from .serializers import (CategoryOfJobCreateSerializer,
                          CategoryOfJobUpdateSerializer, JobCreateSerializer,
                          TgUserSerializer)


class CategoriesList(generics.ListCreateAPIView):
    """
    GET method returns list of all categories

    POST method allows to create new category
    """

    queryset = CategoryOfJob.objects.all()
    serializer_class = CategoryOfJobCreateSerializer


class CategoryRetrieveUpdate(generics.RetrieveUpdateAPIView):
    queryset = CategoryOfJob.objects.all()
    serializer_class = CategoryOfJobUpdateSerializer


class JobCreate(generics.CreateAPIView):
    queryset = Job.objects.all()
    serializer_class = JobCreateSerializer


class JobListByCategory(generics.ListAPIView):
    serializer_class = JobCreateSerializer

    def get_queryset(self):
        queryset = Job.objects.all().filter(category=self.kwargs.get("category"))
        return queryset


class TgUserList(generics.ListCreateAPIView):
    queryset = TgUser.objects.all()
    serializer_class = TgUserSerializer


class TgUserDetail(generics.RetrieveAPIView):
    queryset = TgUser.objects.all()
    serializer_class = TgUserSerializer
    lookup_field = "telegram_id"
