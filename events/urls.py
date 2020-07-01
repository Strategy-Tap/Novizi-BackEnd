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
    attendee_list,
    attendee_settings,
    event_organizers_settings,
    list_of_tag,
    old_event_list,
    session_settings,
    sign_up_to_event,
    speakers_list,
)

app_name = "events"

urlpatterns = [
    path("tags/", list_of_tag),
    path("", EventListCreateAPIView.as_view()),
    path("old/", old_event_list),
    path("<slug>/signup/", sign_up_to_event),
    path("<event_slug>/attendees/", attendee_list),
    path("<event_slug>/speakers/", speakers_list),
    path("<event_slug>/denied/", DeniedSessionListAPIView.as_view()),
    path("<event_slug>/sessions/", SessionListAPIView.as_view()),
    path("<event_slug>/proposers/", ProposerListCreateAPIView.as_view()),
    path("<event_slug>/denied/<slug>/", DeniedSessionRetrieveAPIView.as_view(),),
    path("<event_slug>/sessions/<slug>/", SessionRetrieveAPIView.as_view(),),
    path(
        "<event_slug>/proposers/<slug>/",
        ProposerRetrieveUpdateDestroyAPIView.as_view(),
    ),
    path("<event_slug>/settings/attendee/", attendee_settings),
    path("<event_slug>/settings/organizers/", event_organizers_settings),
    path("<event_slug>/settings/session/<slug>/", session_settings),
    path("<slug>/", EventRetrieveUpdateDestroyAPIView.as_view()),
]
