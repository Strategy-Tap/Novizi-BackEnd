"""Collection views."""
from typing import Any, Dict, List, Tuple

from django.contrib.auth import get_user_model
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import exceptions, generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response

from . import filter
from . import permissions as custom_permissions
from . import serializers
from .models import Attendee, Event, Session, Tag


@api_view(["GET"])
def list_of_tag(request: Request) -> Response:
    """List API Point for tag model."""
    tags = Tag.objects.all()
    serializer = serializers.TagSerializer(tags, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def sign_up_to_event(request: Request, slug: str) -> Response:
    """Let users to signup to an event."""
    event = get_object_or_404(Event, slug=slug)
    if event.hosted_by == request.user:
        raise exceptions.APIException(
            f"You are the owner of the {event.title}.", code=status.HTTP_400_BAD_REQUEST
        )
    if event.attendees.filter(user=request.user).first():
        raise exceptions.APIException(
            f"You already attended the {event.title}.", code=status.HTTP_400_BAD_REQUEST
        )
    if event.event_date < timezone.now():
        raise exceptions.APIException(
            "The registrations time is finished.", code=status.HTTP_400_BAD_REQUEST
        )

    Attendee(user=request.user, events=event).save()
    return Response(status=status.HTTP_201_CREATED)


@api_view(["GET"])
def old_event_list(request: Request) -> Response:
    """Get list of old events."""
    events = (
        Event.objects.select_related("hosted_by")
        .prefetch_related("tags")
        .filter(event_date__lt=timezone.now())
    )

    serializer = serializers.EventListSerializer(events, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


class EventListCreateAPIView(generics.ListCreateAPIView):
    """Event API view for create and list."""

    queryset = (
        Event.objects.select_related("hosted_by")
        .prefetch_related("tags")
        .filter(event_date__gt=timezone.now())
    )

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)

    filterset_class = filter.EventFilter

    search_fields = ("title", "description")

    ordering = ("event_date",)

    ordering_fields = ("total_guest", "event_date", "read_time")

    def get_serializer_class(
        self: "EventListCreateAPIView", *args: Tuple, **kwargs: Any
    ) -> Any:
        """Return the class to use for the serializer."""
        if self.request.method == "POST":

            return serializers.EventCreateUpdateSerializer

        else:
            return serializers.EventListSerializer

    def perform_create(self: "EventListCreateAPIView", serializer: Any) -> None:
        """Method called when the create method called."""
        serializer.save(hosted_by=self.request.user)


class EventRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Event API view for retrieve, update, and delete."""

    queryset = (
        Event.objects.select_related("hosted_by")
        .prefetch_related("organizers", "tags")
        .all()
    )
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        custom_permissions.IsOwnerOrReadOnly,
    )

    lookup_field = "slug"

    def get_serializer_class(
        self: "EventListCreateAPIView", *args: Tuple, **kwargs: Any
    ) -> Any:
        """Return the class to use for the serializer."""
        if self.request.method == "GET":

            return serializers.EventRetrieveSerializer

        else:
            return serializers.EventCreateUpdateSerializer

    def retrieve(
        self: "EventRetrieveUpdateDestroyAPIView",
        request: Request,
        *args: Tuple,
        **kwargs: Dict,
    ) -> Response:
        """Event retrieve endpoint."""
        try:
            event = self.get_queryset().get(slug=kwargs.get("slug"))

        except Exception:
            raise exceptions.NotFound()

        serializer = self.get_serializer(event)

        data = serializer.data

        if request.user.is_authenticated and event.attendees.filter(user=request.user):
            data.update({"has_sign_up": True})

        else:
            data.update({"has_sign_up": False})

        data.update(
            {
                "event_is_open": event.event_date > timezone.now(),
                "is_authenticated": request.user.is_authenticated,
                "is_stuff": event.hosted_by == request.user
                or event.organizers.filter(username=request.user).first() is not None,
            }
        )
        return Response(data, status=status.HTTP_200_OK)


class ProposerListCreateAPIView(generics.ListCreateAPIView):
    """Proposer API view for create and list."""

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    filter_backends = (OrderingFilter, SearchFilter)

    search_fields = ("title", "description")
    ordering = ("title",)

    ordering_fields = ("title", "session_type")

    def get_queryset(self: "ProposerListCreateAPIView") -> List[Session]:
        """Override get_queryset."""
        return Session.objects.filter(status="Draft").filter(
            events__slug=self.kwargs.get("event_slug")
        )

    def get_serializer_class(
        self: "ProposerListCreateAPIView", *args: Tuple, **kwargs: Any
    ) -> Any:
        """Return the class to use for the serializer."""
        if self.request.method == "POST":

            return serializers.SessionRetrieveCreateUpdateSerializer

        else:
            return serializers.SessionListSerializer

    def perform_create(self: "ProposerListCreateAPIView", serializer: Any) -> None:
        """Method called when the create method called."""
        event = get_object_or_404(Event, slug=self.kwargs.get("event_slug"))
        serializer.save(proposed_by=self.request.user, events=event)


class ProposerRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Proposer API view for retrieve, update, and delete."""

    serializer_class = serializers.SessionRetrieveCreateUpdateSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        custom_permissions.IsProposerOrReadOnly,
    )

    lookup_field = "slug"

    def get_queryset(self: "ProposerRetrieveUpdateDestroyAPIView") -> List[Session]:
        """Override get_queryset."""
        return Session.objects.filter(status="Draft").filter(
            events__slug=self.kwargs.get("event_slug")
        )


class SessionListAPIView(generics.ListAPIView):
    """Session API view for accepted session list."""

    serializer_class = serializers.SessionListSerializer

    filter_backends = (OrderingFilter, SearchFilter)

    search_fields = ("title", "description")

    ordering = ("title",)

    ordering_fields = ("title", "session_type")

    def get_queryset(self: "SessionListAPIView") -> List[Session]:
        """Override get_queryset."""
        return Session.objects.filter(status="Accepted").filter(
            events__slug=self.kwargs.get("event_slug")
        )


class SessionRetrieveAPIView(generics.RetrieveAPIView):
    """Session API view for accepted session retrieve."""

    serializer_class = serializers.SessionRetrieveCreateUpdateSerializer

    lookup_field = "slug"

    def get_queryset(self: "SessionRetrieveAPIView") -> List[Session]:
        """Override get_queryset."""
        return Session.objects.filter(status="Accepted").filter(
            events__slug=self.kwargs.get("event_slug")
        )


class DeniedSessionListAPIView(generics.ListAPIView):
    """Session API view for denied session list."""

    serializer_class = serializers.SessionListSerializer

    filter_backends = (OrderingFilter, SearchFilter)

    search_fields = ("title", "description")

    ordering = ("title",)

    ordering_fields = ("title", "session_type")

    def get_queryset(self: "DeniedSessionListAPIView") -> List[Session]:
        """Override get_queryset."""
        return Session.objects.filter(status="Denied").filter(
            events__slug=self.kwargs.get("event_slug")
        )


class DeniedSessionRetrieveAPIView(generics.RetrieveAPIView):
    """Session API view for denied session retrieve."""

    serializer_class = serializers.SessionRetrieveCreateUpdateSerializer

    lookup_field = "slug"

    def get_queryset(self: "DeniedSessionRetrieveAPIView") -> List[Session]:
        """Override get_queryset."""
        return Session.objects.filter(status="Denied").filter(
            events__slug=self.kwargs.get("event_slug")
        )


@api_view(["GET"])
def attendee_list(request: Request, event_slug: str) -> Response:
    """Get list of attendee in the event."""
    event = get_object_or_404(Event, slug=event_slug)
    attendees = event.attendees.all()
    serializer = serializers.AttendeeSerializer(attendees, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def speakers_list(request: Request, event_slug: str) -> Response:
    """Get list of speaker in the event."""
    event = get_object_or_404(Event, slug=event_slug)
    sessions = event.sessions.filter(status="Accepted")
    serializer = serializers.SpeakerSerializer(sessions, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def session_settings(request: Request, event_slug: str, slug: str) -> Response:
    """Settings for a session to Accepted or Draft or Denied.

    Args:
        request: Request object
        event_slug: The event slug.
        slug: The session slug

    Examples:
        {"status": "Accepted"}

    Returns:
        Response: Json response.
        200: if everything is correct.
        404: if the event or the session doesn't exists,
        and if user don't have permission.
    """
    event = get_object_or_404(Event, slug=event_slug)
    if event.hosted_by == request.user and event.event_date > timezone.now():
        session = event.sessions.filter(slug=slug).first()

        serializer = serializers.SessionSettingSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True) and session:
            session.status = serializer.data.get("status")
            session.save()
            return Response(
                {"detail": f"{session} has been {serializer.data.get('status')}"},
                status=status.HTTP_200_OK,
            )

    return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def attendee_settings(request: Request, event_slug: str) -> Response:
    """Settings for a attendee to check if they attended the event or not.

    Args:
        request: Request object
        event_slug: The event slug.

    Examples:
        {"list_of_username": ["novizi", "novizi2"]}

    Returns:
        Response: Json response.
        200: if everything is correct.
        404: if the event or user doesn't exists
        and if user don't have permission.
    """
    event = get_object_or_404(Event, slug=event_slug)

    if (
        event.hosted_by == request.user
        or event.organizers.filter(username=request.user).first()
        and event.event_date > timezone.now()
    ):

        serializer = serializers.AttendeeSettingSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):

            for username in serializer.data.get("list_of_username"):
                user = get_object_or_404(get_user_model(), username=username)
                attendee = event.attendees.filter(user=user).first()

                if attendee:
                    attendee.has_attended = True
                    attendee.save()

            return Response(status=status.HTTP_200_OK)

    return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def event_organizers_settings(request: Request, event_slug: str) -> Response:
    """Settings for a organizers to to Add or Remove organizer.

    Args:
        request: Request object
        event_slug: The event slug.

    Examples:
        {"list_of_username": ["novizi"], "action": "Add"}

    Returns:
        Response: Json response.
        200: if everything is correct.
        404: if the event or user doesn't exists
        and if user don't have permission.
    """
    event = get_object_or_404(Event, slug=event_slug)

    if event.hosted_by == request.user and event.event_date > timezone.now():

        serializer = serializers.OrganizersSettingSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):

            for username in serializer.data.get("list_of_username"):
                user = get_object_or_404(get_user_model(), username=username)

                if serializer.data.get("action") == "Add":
                    event.organizers.add(user)

                if serializer.data.get("action") == "Remove":
                    event.organizers.remove(user)

            return Response(status=status.HTTP_200_OK)

    return Response(status=status.HTTP_404_NOT_FOUND)
