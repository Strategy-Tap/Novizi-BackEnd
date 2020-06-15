"""Admin module for events app."""
from django.contrib import admin
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import QuerySet
from import_export import resources
from import_export.admin import ImportExportActionModelAdmin
from import_export.fields import Field
from leaflet.admin import LeafletGeoAdminMixin

from .forms import AttendeeAdminForm
from .models import Attendee, Event, Session, Tag


class AttendeeResource(resources.ModelResource):
    """ModelResource is Resource subclass for handling Django models."""

    class Meta:
        """Meta data."""

        model = Attendee
        fields = (
            "user__username",
            "user__email",
            "user__full_name",
            "events__title",
            "has_attended",
        )


class EventResource(resources.ModelResource):
    """ModelResource is Resource subclass for handling Django models."""

    total_attendees = Field()
    available_place = Field()
    total_attended = Field()
    total_not_attended = Field()
    total_sessions = Field()
    total_draft_sessions = Field()
    total_accepted_sessions = Field()
    total_denied_sessions = Field()
    total_talk = Field()
    total_lighting_talk = Field()
    total_workshop = Field()

    class Meta:
        """Meta data."""

        model = Event
        fields = (
            "title",
            "event_date",
            "total_guest",
            "total_attendees",
            "available_place",
            "total_attended",
            "total_not_attended",
            "total_sessions",
            "total_draft_sessions",
            "total_accepted_sessions",
            "total_denied_sessions",
            "total_talk",
            "total_lighting_talk",
            "total_workshop",
        )

        export_order = (
            "title",
            "event_date",
            "total_guest",
            "total_attendees",
            "available_place",
            "total_attended",
            "total_not_attended",
            "total_sessions",
            "total_draft_sessions",
            "total_accepted_sessions",
            "total_denied_sessions",
            "total_talk",
            "total_lighting_talk",
            "total_workshop",
        )

    def dehydrate_total_attendees(self: "EventResource", event: Event) -> int:
        """Computing method to get total attendees."""
        return event.attendees.count()

    def dehydrate_available_place(self: "EventResource", event: Event) -> int:
        """Computing method to get total available place."""
        return event.total_guest - event.attendees.count()

    def dehydrate_total_attended(self: "EventResource", event: Event) -> int:
        """Computing method to get total attended."""
        return event.attendees.filter(has_attended=True).count()

    def dehydrate_total_not_attended(self: "EventResource", event: Event) -> int:
        """Computing method to get total not attended."""
        return event.attendees.filter(has_attended=False).count()

    def dehydrate_total_sessions(self: "EventResource", event: Event) -> int:
        """Computing method to get total sessions."""
        return event.sessions.count()

    def dehydrate_total_draft_sessions(self: "EventResource", event: Event) -> int:
        """Computing method to get total draft sessions."""
        return event.sessions.filter(status="Draft").count()

    def dehydrate_total_accepted_sessions(self: "EventResource", event: Event) -> int:
        """Computing method to get total accepted sessions."""
        return event.sessions.filter(status="Accepted").count()

    def dehydrate_total_denied_sessions(self: "EventResource", event: Event) -> int:
        """Computing method to get total denied sessions."""
        return event.sessions.filter(status="Denied").count()

    def dehydrate_total_talk(self: "EventResource", event: Event) -> int:
        """Computing method to get total talk."""
        return event.sessions.filter(session_type="Talk", status="Accepted").count()

    def dehydrate_total_lighting_talk(self: "EventResource", event: Event) -> int:
        """Computing method to get total lighting talk."""
        return event.sessions.filter(
            session_type="Lighting Talk", status="Accepted"
        ).count()

    def dehydrate_total_workshop(self: "EventResource", event: Event) -> int:
        """Computing method to get total workshop."""
        return event.sessions.filter(session_type="WorkShop", status="Accepted").count()


@admin.register(Attendee)
class AttendeeAdmin(ImportExportActionModelAdmin):
    """Configure the attendee model in admin page."""

    resource_class = AttendeeResource

    form = AttendeeAdminForm

    date_hierarchy = "events__event_date"

    list_display = (
        "user",
        "get_email",
        "get_full_name",
        "events",
        "has_attended",
    )

    list_filter = ("has_attended",)

    search_fields = ("user__username",)

    actions = ["make_has_attended", "make_has_not_attended"]

    def get_full_name(self: "AttendeeAdmin", obj: Attendee) -> str:
        """Computing method to get full name."""
        return obj.user.full_name

    def get_email(self: "AttendeeAdmin", obj: Attendee) -> str:
        """Computing method to get full name."""
        return obj.user.email

    def make_has_attended(
        self: "AttendeeAdmin", request: WSGIRequest, queryset: QuerySet
    ) -> None:
        """Custom action that update the status to attended."""
        queryset.update(has_attended=True)

    def make_has_not_attended(
        self: "AttendeeAdmin", request: WSGIRequest, queryset: QuerySet
    ) -> None:
        """Custom action that update the status to not attended."""
        queryset.update(has_attended=False)

    make_has_attended.short_description = "Mark selected Attendee as Attended"
    make_has_not_attended.short_description = "Mark selected Attendee as not Attended"

    get_email.short_description = "Email"
    get_full_name.short_description = "Full name"


@admin.register(Event)
class EventAdmin(LeafletGeoAdminMixin, ImportExportActionModelAdmin):
    """Configure the event model in admin page."""

    resource_class = EventResource
    date_hierarchy = "event_date"
    list_display = (
        "title",
        "event_date",
        "total_guest",
        "total_attendees",
        "available_place",
        "total_attended",
        "total_not_attended",
        "total_sessions",
        "total_draft_sessions",
        "total_accepted_sessions",
        "total_denied_sessions",
        "total_talk",
        "total_lighting_talk",
        "total_workshop",
    )
    list_filter = ["event_date"]
    search_fields = ["title", "description"]
    readonly_fields = ("slug", "read_time")


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    """Configure the session model in admin page."""

    date_hierarchy = "events__event_date"

    list_display = ("title", "proposed_by", "session_type", "events", "status")

    list_filter = ("session_type", "proposed_by", "events__title", "events__event_date")

    search_fields = ("title", "description")

    actions = ["make_accepted", "make_denied"]

    readonly_fields = ("slug",)

    def make_accepted(
        self: "SessionAdmin", request: WSGIRequest, queryset: QuerySet
    ) -> None:
        """Custom action that update the status of session to Accepted."""
        queryset.update(status="Accepted")

    def make_denied(
        self: "SessionAdmin", request: WSGIRequest, queryset: QuerySet
    ) -> None:
        """Custom action that update the status of session to Denied."""
        queryset.update(status="Denied")

    make_accepted.short_description = "Mark selected sessions as Accepted"
    make_denied.short_description = "Mark selected sessions as Denied"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Configure the tag model in admin page."""

    list_display = ("name", "total_events")
