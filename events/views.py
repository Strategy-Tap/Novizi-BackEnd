"""Collection views."""
from typing import Any, Dict, Tuple

from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response

from . import filter
from . import permissions as custom_permissions
from . import serializers
from .models import Event, Tag


class EventsViewSet(viewsets.ModelViewSet):
    """ModelViewSet for events."""

    queryset = Event.objects.filter(event_date__gt=timezone.now())

    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)

    filterset_class = filter.EventFilter

    search_fields = ("title", "description")

    ordering = ("event_date",)

    ordering_fields = ("total_guest", "event_date", "read_time")

    lookup_field = "slug"

    def get_serializer_class(self: "EventsViewSet", *args: Tuple, **kwargs: Any) -> Any:
        """Return the class to use for the serializer."""
        if self.action == "retrieve":
            return serializers.EventRetrieveSerializer

        if self.action in ["update", "partial_update", "create"]:
            return serializers.EventCreateUpdateSerializer

        return serializers.EventListSerializer

    def get_permissions(self: "EventsViewSet") -> Any:
        """Return list of classes to use for the permissions."""
        if self.action == "create":

            permission_classes = (permissions.IsAuthenticated,)

        elif self.action in ["update", "partial_update", "destroy"]:

            permission_classes = (
                permissions.IsAuthenticatedOrReadOnly,
                custom_permissions.IsOwnerOrReadOnly,
            )

        else:

            permission_classes = [permissions.IsAuthenticatedOrReadOnly]

        return [permission() for permission in permission_classes]

    def perform_create(self: "EventsViewSet", serializer: Any) -> None:
        """Method called when the create method called."""
        serializer.save(hosted_by=self.request.user)

    def retrieve(
        self: "EventsViewSet", request: Request, *args: Tuple, **kwargs: Dict
    ) -> Response:
        """Event retrieve endpoint."""
        event = get_object_or_404(Event, slug=kwargs.get("slug"))

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


@api_view(["GET"])
def list_of_tag(request: Request) -> Response:
    """List API Point for tag model."""
    tags = Tag.objects.all()
    serializer = serializers.TagSerializer(tags, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
