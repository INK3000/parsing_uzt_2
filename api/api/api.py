from typing import Any

from django.core.serializers import serialize
from django.db.utils import IntegrityError
from django.http import JsonResponse
from django.shortcuts import get_list_or_404, get_object_or_404
from ninja import NinjaAPI
from ninja.security import APIKeyHeader
from pydantic.error_wrappers import ValidationError

from . import models
from . import schemas as scm


class ApiKeyAuth(APIKeyHeader):
    param_name = 'X-API-Key'

    def authenticate(self, request, key):
        if models.Token.objects.filter(key=key).exists():
            return key


api = NinjaAPI(auth=ApiKeyAuth())


# Manage Category ****************************************
@api.get('/categories', response=list[scm.CategoryOut])
def categories_list(request):
    return get_list_or_404(models.Category)


@api.post(
    '/categories/create', response={201: list[scm.CategoryOut], 409: scm.Error}
)
def category_create(request, payload: list[scm.CategoryIn]):
    category_list = [models.Category(**item.dict()) for item in payload]
    try:
        created_list = models.Category.objects.bulk_create(category_list)
        return 201, created_list
    except IntegrityError as err:
        return 409, {'detail': f'{err}'}


# Manage Jobs **************************************
@api.post(
    'category/{category_id}/jobs/create',
    response={201: list[scm.JobOut], 409: scm.Error},
)
def jobs_bulk_create(request, category_id: int, payload: list[scm.JobIn]):
    exist_set = set(models.Job.objects.all().filter(category=category_id))
    bulk_set = {
        models.Job(category_id=category_id, **item.dict()) for item in payload
    }
    only_new_set = bulk_set.difference(exist_set)
    created_jobs = models.Job.objects.bulk_create(only_new_set)
    if created_jobs:
        created_jobs.sort(key=lambda item: item.id, reverse=True)
        return 201, created_jobs
    else:
        return 409, {'detail': 'There were no new data for this category'}


@api.get('category/{category_id}/jobs', response=list[scm.JobOut])
def jobs_by_category(request, category_id: int):
    queryset_list = get_list_or_404(models.Job, category=category_id)
    return queryset_list


# Manage Subscribers **************************************
@api.get('/subscribers', response=list[scm.SubscriberOut])
def subscribers_list(request):
    return get_list_or_404(models.Subscriber)


@api.get('/subscriber/create/{telegram_id}', response=scm.SubscriberOut)
def subscriber_create(request, telegram_id: int):
    subscriber = models.Subscriber(telegram_id=telegram_id)
    try:
        subscriber.save()
        return subscriber
    except IntegrityError as err:
        data = {'details': f'{err}'}
        return JsonResponse(data=data, status=409)


@api.post('/subscriber/update', response=scm.SubscriberOut)
def subscriber_update(request, payload: scm.SubscriberUpdate):
    telegram_id = payload.telegram_id
    subscriber = get_object_or_404(models.Subscriber, telegram_id=telegram_id)
    queryset = models.Subscription.objects.all().filter(subscriber=subscriber)

    # If there is an IntegrityError, we can restore all user subscriptions
    old_data = subscriber.subscriptions.values('category_id', 'date_last_sent')
    old_subscriptions = [
        models.Subscription(subscriber=subscriber, **item) for item in old_data
    ]

    queryset.delete()

    new_subscriptions = [
        models.Subscription(subscriber=subscriber, **item.dict())
        for item in payload.subscriptions
    ]
    try:
        models.Subscription.objects.bulk_create(new_subscriptions)
        return subscriber
    except IntegrityError as err:
        models.Subscription.objects.bulk_create(old_subscriptions)
        data = {'details': f'{err}'}
        return JsonResponse(data=data, status=409)


@api.get('/subscriber/{telegram_id}', response=scm.SubscriberOut)
def get_subscriber(request, telegram_id: int):
    subscriber = get_object_or_404(models.Subscriber, telegram_id=telegram_id)
    return subscriber
