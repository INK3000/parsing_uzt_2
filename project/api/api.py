from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from ninja import NinjaAPI

from .models import Category
from .schemas import (CategorySchemaIn, CategorySchemaOut,
                      CategorySchemaUpdate, Error)

api = NinjaAPI()


@api.get("/categories", response=list[CategorySchemaOut])
def categories_list(request):
    queryset = Category.objects.all()
    return list(queryset)


@api.put("/category/update", response=CategorySchemaOut)
def category_update(request, payload: CategorySchemaUpdate):
    category = get_object_or_404(Category, id=payload.dict().get("id"))
    for attr, value in payload.dict().items():
        setattr(category, attr, value)
    category.save()
    return category


@api.post("/category/create", response={201: CategorySchemaOut, 409: Error})
def category_create(request, payload: CategorySchemaIn):
    category = Category(**payload.dict())
    try:
        category.save()
        return 201, category
    except IntegrityError as err:
        return 409, {"detail": f"{err}"}
