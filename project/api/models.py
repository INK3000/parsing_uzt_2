from django.db import models


class Tg_User(models.Model):
    telegram_id = models.CharField(max_length=12)
    subscriptions = models.TextField()


class Category_of_job(models.Model):
    name = models.CharField(max_length=255)
    event_target = models.CharField(max_length=255)
    last_id = models.IntegerField()

    def __str__(self):
        return f"{self.name}"


class Job(models.Model):
    date_upd = models.DateField()
    name = models.TextField()
    category = models.ForeignKey(
        Category_of_job, on_delete=models.SET_NULL, null=True)
    company = models.CharField(max_length=255)
    date_from = models.DateField()
    date_to = models.DateField()
    place = models.CharField(max_length=255)
    url = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} - {self.company} - {self.category.name}"
