"""Collection of serializers."""
from typing import Dict

from pydantic import BaseModel
from rest_framework import exceptions, serializers

from .models import Event, Session, Tag


class GeoLocation(BaseModel):
    """Pydantic model for Geo location."""

    geom: Dict


class ProfileSerializer(serializers.Serializer):
    """Serializer to get username and picture of owner of the event."""

    username = serializers.CharField(read_only=True)

    picture = serializers.ImageField(read_only=True)


class AttendeeSerializer(serializers.Serializer):
    """Serializer For attendees."""

    user = ProfileSerializer(read_only=True)


class SpeakerSerializer(serializers.Serializer):
    """Serializer For attendees."""

    proposed_by = ProfileSerializer(read_only=True)


class TagSerializer(serializers.Serializer):
    """Tag serializer."""

    name = serializers.CharField(read_only=True)
    total_events = serializers.IntegerField(read_only=True)


class TagStringSerializer(serializers.StringRelatedField):
    """A string serializer that convert string to object id."""

    def to_internal_value(self: "TagStringSerializer", data: str) -> int:
        """Getting the string value changed into object id.

        Args:
            data: the text to convert.

        Returns:
            the object id.
        """
        tag, created = Tag.objects.get_or_create(name=data.lower())

        return tag.id


class EventListSerializer(serializers.Serializer):
    """Event List Serializer."""

    title = serializers.CharField(read_only=True)

    event_date = serializers.DateTimeField(read_only=True)

    total_guest = serializers.IntegerField(read_only=True)

    available_place = serializers.IntegerField(read_only=True)

    read_time = serializers.IntegerField(read_only=True)

    slug = serializers.SlugField(read_only=True)

    cover = serializers.ImageField(read_only=True)

    hosted_by = ProfileSerializer(read_only=True)

    tags = serializers.StringRelatedField(read_only=True, many=True)


class EventRetrieveSerializer(serializers.Serializer):
    """Event Retrieve Serializer."""

    title = serializers.CharField(read_only=True)

    description = serializers.CharField(read_only=True)

    read_time = serializers.IntegerField(read_only=True)

    event_date = serializers.DateTimeField(read_only=True)

    total_guest = serializers.IntegerField(read_only=True)

    hosted_by = ProfileSerializer(read_only=True)

    cover = serializers.ImageField(read_only=True)

    tags = serializers.StringRelatedField(read_only=True, many=True)

    organizers = ProfileSerializer(read_only=True, many=True)

    total_attendees = serializers.IntegerField(read_only=True)

    available_place = serializers.IntegerField(read_only=True)

    total_attended = serializers.IntegerField(read_only=True)

    total_not_attended = serializers.IntegerField(read_only=True)

    total_sessions = serializers.IntegerField(read_only=True)

    total_draft_sessions = serializers.IntegerField(read_only=True)

    total_accepted_sessions = serializers.IntegerField(read_only=True)

    total_denied_sessions = serializers.IntegerField(read_only=True)

    total_talk = serializers.IntegerField(read_only=True)

    total_lighting_talk = serializers.IntegerField(read_only=True)

    total_workshop = serializers.IntegerField(read_only=True)

    geom = serializers.JSONField(read_only=True)


class EventCreateUpdateSerializer(serializers.ModelSerializer):
    """Event Create Update Serializer."""

    tags = TagStringSerializer(many=True)

    cover = serializers.ImageField(required=False)

    geom = serializers.JSONField()

    def validate(self: "EventCreateUpdateSerializer", data: Dict) -> Dict:
        """Extra validation."""
        try:
            GeoLocation(geom=data["geom"])
        except Exception:
            raise exceptions.ParseError("geom field should be json")

        return data

    class Meta:
        """Meta data."""

        model = Event
        fields = (
            "title",
            "description",
            "cover",
            "total_guest",
            "event_date",
            "tags",
            "geom",
        )


class SessionRetrieveCreateUpdateSerializer(serializers.ModelSerializer):
    """Session Retrieve Create Update Serializer."""

    status = serializers.CharField(read_only=True)
    proposed_by = ProfileSerializer(read_only=True)

    class Meta:
        """Meta data."""

        model = Session
        fields = ("title", "description", "session_type", "status", "proposed_by")


class SessionListSerializer(serializers.Serializer):
    """Session List Serializer."""

    title = serializers.CharField(read_only=True)

    session_type = serializers.CharField(read_only=True)

    slug = serializers.SlugField(read_only=True)

    proposed_by = ProfileSerializer(read_only=True)
