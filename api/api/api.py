from django.db.utils import IntegrityError
from django.shortcuts import get_list_or_404, get_object_or_404
from ninja import NinjaAPI

from . import models
from . import schemas as scm

api = NinjaAPI()


# Manage Category ****************************************
@api.get("/categories", response=list[scm.CategoryOut])
def categories_list(request):
    queryset = models.Category.objects.all()
    return list(queryset)


@api.post("/categories/create", response={201: list[scm.CategoryOut], 409: scm.Error})
def category_create(request, payload: list[scm.CategoryIn]):
    category_list = [models.Category(**item.dict()) for item in payload]
    try:
        created_list = models.Category.objects.bulk_create(category_list)
        return 201, created_list
    except IntegrityError as err:
        return 409, {"detail": f"{err}"}


@api.post("/category/{category_id}/update", response=scm.CategoryOut)
def category_update(request, category_id: int, payload: scm.CategoryUpdate):
    category = get_object_or_404(models.Category, id=category_id)
    for attr, value in payload.dict().items():
        setattr(category, attr, value)
    category.save()
    return category


# Manage Jobs **************************************
@api.post(
    "category/{category_id}/jobs/create",
    response={201: list[scm.JobOut], 409: scm.Error},
)
def jobs_bulk_create(request, category_id: int, payload: list[scm.JobIn]):
    exist_set = set(models.Job.objects.all().filter(category=category_id))
    bulk_set = {models.Job(category_id=category_id, **item.dict())
                for item in payload}
    only_new_set = bulk_set.difference(exist_set)
    created_jobs = models.Job.objects.bulk_create(only_new_set)
    if created_jobs:
        created_jobs.sort(key=lambda item: item.id, reverse=True)
        return 201, created_jobs
    else:
        return 409, {"detail": "There were no new data for this category"}


@api.get("category/{category_id}/jobs", response=list[scm.JobOut])
def jobs_by_category(request, category_id: int):
    queryset_list = get_list_or_404(models.Job, category=category_id)
    return queryset_list


# Manage Subscribers **************************************
@api.get("/subscribers", response=list[scm.SubscriberOut])
def subscribers_list(request):
    queryset = models.Subscriber.objects.all()
    return list(queryset)


@api.post("/subscriber/create", response={201: scm.SubscriberOut, 409: scm.Error})
def subscriber_create(request, payload: scm.SubscriberIn):
    subscriber = models.Subscriber(**payload.dict())
    try:
        subscriber.save()
        return 201, subscriber
    except IntegrityError as err:
        return 409, {"detail": f"{err}"}


@api.post("/subscriber/update", response=scm.SubscriberOut)
def subscriber_update(request, payload: scm.SubscriberIn):
    subscriber = get_object_or_404(
        models.Subscriber, telegram_id=payload.telegram_id)
    subscriber.data = payload.data
    subscriber.save()
    return subscriber
