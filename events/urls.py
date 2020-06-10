"""Events URL Configuration."""
from django.urls import path

from .views import (
    EventListCreateAPIView,
    EventRetrieveUpdateDestroyAPIView,
    list_of_tag,
    sign_up_to_event,
)

app_name = "events"

urlpatterns = [
    path("tags/", list_of_tag),
    path("", EventListCreateAPIView.as_view()),
    path("<slug>/signup/", sign_up_to_event),
    path("<slug>/", EventRetrieveUpdateDestroyAPIView.as_view()),
]
