"""Collection of filters."""
from django_filters import rest_framework as filters

from .models import Event


class EventFilter(filters.FilterSet):
    """Filter for event model."""

    tags_name = filters.CharFilter("tags__name")

    event_date = filters.DateFromToRangeFilter("event_date")

    class Meta:
        """Meta data."""

        model = Event
        fields = (
            "tags_name",
            "read_time",
            "event_date",
        )
