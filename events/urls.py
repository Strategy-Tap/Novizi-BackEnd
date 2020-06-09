"""Events URL Configuration."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import EventsViewSet, list_of_tag

router = DefaultRouter()

router.register("", EventsViewSet)

app_name = "events"

urlpatterns = [
    path("tags/", list_of_tag),
    path("", include(router.urls)),
]
