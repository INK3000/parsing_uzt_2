from django.db import models


class Subscriber(models.Model):
    telegram_id = models.PositiveIntegerField(primary_key=True)
    date_created = models.DateField(auto_now_add=True)
    json_data = models.TextField(default="", blank=True)

    class Meta:
        ordering = ["-date_created"]

    def __str__(self):
        return str(self.telegram_id)


class Category(models.Model):
    name = models.CharField(max_length=255)
    href = models.CharField(max_length=255, unique=True)
    last_id = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-id"]
        verbose_name = "Category"

    def __str__(self):
        return f"{self.name}"


class Job(models.Model):
    date_upd = models.DateField(auto_now_add=True)
    name = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    company = models.CharField(max_length=255)
    date_from = models.DateField()
    date_to = models.DateField()
    place = models.CharField(max_length=255)
    url = models.CharField(max_length=255)

    class Meta:
        ordering = ["-id"]
        constraints = [
            models.UniqueConstraint(name="category_url", fields=["category", "url"])
        ]

    def __str__(self):
        return f"id:{self.id} {self.name} - {self.company} - {self.category.name}"

    def __eq__(self, other):
        return self.category == other.category and self.url == other.url

    def __hash__(self):
        return hash((self.category, self.url))
