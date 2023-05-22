from django.contrib.auth.models import User
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255)
    href = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ['-id']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return f'{self.id}: {self.name}'


class Job(models.Model):
    date_scraped = models.DateTimeField(auto_now_add=True)
    title = models.TextField()
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True
    )
    company = models.CharField(max_length=255)
    date_from = models.DateField()
    date_to = models.DateField()
    place = models.CharField(max_length=255)
    url = models.CharField(max_length=255)

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                name='category_url', fields=['category', 'url']
            )
        ]

    def __str__(self):
        return f'id:{self.id} {self.title} - {self.company} - {self.category.name}'

    def __eq__(self, other):
        return self.category == other.category and self.url == other.url

    def __hash__(self):
        return hash((self.category, self.url))


class Subscriber(models.Model):
    telegram_id = models.PositiveIntegerField(unique=True)
    date_created = models.DateField(auto_now_add=True)
    subscribed_to = models.ManyToManyField('Category', through='Subscription')

    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        return str(self.telegram_id)


class Subscription(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subscriber = models.ForeignKey(
        Subscriber, on_delete=models.CASCADE, related_name='subscriptions'
    )
    date_last_sent = models.DateTimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='user_and_category',
                fields=['category_id', 'subscriber_id'],
            )
        ]

    def __str__(self):
        return f'Telegram user:{self.subscriber.telegram_id} Category id: {self.category.name}'
