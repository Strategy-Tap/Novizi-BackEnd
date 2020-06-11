"""Events URL Configuration."""
from django.urls import path

from .views import (
    DeniedSessionListAPIView,
    DeniedSessionRetrieveAPIView,
    EventListCreateAPIView,
    EventRetrieveUpdateDestroyAPIView,
    ProposerListCreateAPIView,
    ProposerRetrieveUpdateDestroyAPIView,
    SessionListAPIView,
    SessionRetrieveAPIView,
    list_of_tag,
    sign_up_to_event,
)

app_name = "events"

urlpatterns = [
    path("tags/", list_of_tag),
    path("", EventListCreateAPIView.as_view()),
    path("<slug>/signup/", sign_up_to_event),
    path("<event_slug>/denied/", DeniedSessionListAPIView.as_view()),
    path("<event_slug>/sessions/", SessionListAPIView.as_view()),
    path("<event_slug>/proposers/", ProposerListCreateAPIView.as_view()),
    path("<event_slug>/denied/<slug>/", DeniedSessionRetrieveAPIView.as_view(),),
    path("<event_slug>/sessions/<slug>/", SessionRetrieveAPIView.as_view(),),
    path(
        "<event_slug>/proposers/<slug>/",
        ProposerRetrieveUpdateDestroyAPIView.as_view(),
    ),
    path("<slug>/", EventRetrieveUpdateDestroyAPIView.as_view()),
]
