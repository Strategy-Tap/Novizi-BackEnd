"""Collection views."""
from typing import Any, Dict, Tuple

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
    Attendee(user=request.user, events=event).save()
    return Response(status=status.HTTP_201_CREATED)


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
            }
        )
        return Response(data, status=status.HTTP_200_OK)


class ProposerListCreateAPIView(generics.ListCreateAPIView):
    """Proposer API view for create and list."""

    queryset = Session.objects.filter(status="Draft")

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    filter_backends = (OrderingFilter, SearchFilter)

    search_fields = ("title", "description")
    ordering = ("title",)

    ordering_fields = ("title", "session_type")

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

    queryset = Session.objects.filter(status="Draft")
    serializer_class = serializers.SessionRetrieveCreateUpdateSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        custom_permissions.IsProposerOrReadOnly,
    )

    lookup_field = "slug"
