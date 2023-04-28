from .models import CategoryOfJob, Job, TgUser
from .serializers import CategoryOfJobSerializer, JobSerializer, TgUserSerializer
from rest_framework import generics


class CategoriesList(generics.ListAPIView):
    queryset = CategoryOfJob.objects.all()
    serializer_class = CategoryOfJobSerializer


class JobList(generics.ListAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer


class TgUserList(generics.ListAPIView):
    queryset = TgUser.objects.all()
    serializer_class = TgUserSerializer
