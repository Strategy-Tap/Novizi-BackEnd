"""Collection of model."""
from typing import Any

from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from .utils import get_read_time, unique_slug


def event_upload_to(instance: "Event", filename: str) -> str:
    """A help Function to change the image upload path.

    Args:
        instance: django model
        filename: the uploaded file name

    Returns:
        path in string format
    """
    return f"images/events/cover/{instance.title}/{filename}"


class Tag(models.Model):
    """Reference tag model."""

    name = models.CharField(verbose_name=_("name"), max_length=200, unique=True)

    class Meta:
        """Meta data."""

        verbose_name = _("tag")
        verbose_name_plural = _("tags")

    def __str__(self: "Tag") -> str:
        """It return readable name for the model."""
        return f"{self.name}"

    def total_events(self: "Tag") -> int:
        """Getting total of events for the tag."""
        return self.events.count()

    total_events.short_description = _("Events")
    total_events.int = 0


class Event(models.Model):
    """Reference event model."""

    title = models.CharField(verbose_name=_("title"), max_length=400)

    description = models.TextField(verbose_name=_("description"))

    read_time = models.IntegerField(default=0, verbose_name=_("read time"))

    slug = models.SlugField(verbose_name=_("slug"), unique=True, blank=True)

    event_date = models.DateTimeField(verbose_name=_("event date"))

    total_guest = models.PositiveIntegerField(
        verbose_name=_("total of guest"), default=1
    )

    hosted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("hosted by"),
        on_delete=models.CASCADE,
        related_name="events",
        db_index=True,
    )

    cover = models.ImageField(
        verbose_name=_("cover"), blank=True, null=True, upload_to=event_upload_to
    )

    tags = models.ManyToManyField(
        to=Tag, verbose_name=_("tags"), related_name="events", blank=True
    )

    organizers = models.ManyToManyField(
        to=settings.AUTH_USER_MODEL,
        verbose_name=_("organizers"),
        related_name="events_organizers",
        blank=True,
    )

    created_at = models.DateTimeField(verbose_name=_("created at"), auto_now_add=True)

    updated_at = models.DateTimeField(verbose_name=_("updated at"), auto_now=True)

    class Meta:
        """Meta data."""

        verbose_name = _("event")

        verbose_name_plural = _("events")

    def __str__(self: "Event") -> str:
        """It return readable name for the model."""
        return f"{self.title}"

    def total_attendees(self: "Event") -> int:
        """Getting total of attendees for the event."""
        return self.attendees.count()

    def available_place(self: "Event") -> int:
        """Getting total of available place for the event."""
        return self.total_guest - self.attendees.count()

    def total_attended(self: "Event") -> int:
        """Getting total of people who actual attended for the event."""
        return self.attendees.filter(has_attended=True).count()

    def total_not_attended(self: "Event") -> int:
        """Getting total of people who didn't attended for the event."""
        return self.attendees.filter(has_attended=False).count()

    def total_sessions(self: "Event") -> int:
        """Getting total of sessions in event."""
        return self.sessions.count()

    def total_draft_sessions(self: "Event") -> int:
        """Getting total of draft sessions in event."""
        return self.sessions.filter(status="Draft").count()

    def total_accepted_sessions(self: "Event") -> int:
        """Getting total of accepted sessions in event."""
        return self.sessions.filter(status="Accepted").count()

    def total_denied_sessions(self: "Event") -> int:
        """Getting total of denied sessions in event."""
        return self.sessions.filter(status="Denied").count()

    def total_talk(self: "Event") -> int:
        """Getting total of talk in event."""
        return self.sessions.filter(session_type="Talk", status="Accepted").count()

    def total_lighting_talk(self: "Event") -> int:
        """Getting total of lighting talk in event."""
        return self.sessions.filter(
            session_type="Lighting Talk", status="Accepted"
        ).count()

    def total_workshop(self: "Event") -> int:
        """Getting total of workshop in event."""
        return self.sessions.filter(session_type="WorkShop", status="Accepted").count()

    total_sessions.short_description = _("Sessions")
    total_draft_sessions.short_description = _("Draft Sessions")
    total_accepted_sessions.short_description = _("Accepted Sessions")
    total_denied_sessions.short_description = _("Denied Sessions")
    total_talk.short_description = _("Talk")
    total_lighting_talk.short_description = _("Lighting Talk")
    total_workshop.short_description = _("Workshop")
    total_attendees.short_description = _("Attendees")
    total_attended.short_description = _("Has Attended")
    total_not_attended.short_description = _("Has Not Attended")
    available_place.short_description = _("Available Place")


class Attendee(models.Model):
    """Reference attendee model."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("user"),
        on_delete=models.CASCADE,
        related_name="attendees",
        db_index=True,
    )

    events = models.ForeignKey(
        Event,
        verbose_name=_("events"),
        on_delete=models.CASCADE,
        related_name="attendees",
        db_index=True,
    )

    has_attended = models.BooleanField(
        verbose_name=_("has attended"), blank=True, null=True
    )

    created_at = models.DateTimeField(verbose_name=_("created at"), auto_now_add=True)

    updated_at = models.DateTimeField(verbose_name=_("updated at"), auto_now=True)

    class Meta:
        """Meta data."""

        verbose_name = _("attendee")

        verbose_name_plural = _("attendees")

    def __str__(self: "Attendee") -> str:
        """It return readable name for the model."""
        return f"{self.user}"


class Session(models.Model):
    """Reference session model."""

    choose_category = (
        ("Talk", _("Talk")),
        ("Lighting Talk", _("Lighting Talk")),
        ("WorkShop", _("WorkShop")),
    )

    choose_status = (
        ("Draft", _("Draft")),
        ("Accepted", _("Accepted")),
        ("Denied", _("Denied")),
    )

    title = models.CharField(verbose_name=_("title"), max_length=400)

    description = models.TextField(verbose_name=_("description"))

    session_type = models.CharField(
        max_length=100, choices=choose_category, verbose_name=_("session type")
    )

    slug = models.SlugField(verbose_name=_("slug"), unique=True, blank=True)

    events = models.ForeignKey(
        Event,
        verbose_name=_("events"),
        on_delete=models.CASCADE,
        related_name="sessions",
        db_index=True,
    )

    status = models.CharField(
        verbose_name=_("status"), max_length=10, choices=choose_status, default="Draft"
    )

    proposed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("proposed by"),
        on_delete=models.CASCADE,
        related_name="sessions",
        db_index=True,
    )

    created_at = models.DateTimeField(verbose_name=_("created at"), auto_now_add=True)

    updated_at = models.DateTimeField(verbose_name=_("updated at"), auto_now=True)

    class Meta:
        """Meta data."""

        verbose_name = _("session")

        verbose_name_plural = _("sessions")

    def __str__(self: "Session") -> str:
        """It return readable name for the model."""
        return f"{self.title}"


@receiver(pre_save, sender=Session)
def session_slug_creator(sender: Session, instance: Session, **kwargs: Any) -> None:
    """Single for Session."""
    if not instance.slug:
        instance.slug = unique_slug(title=instance.title)


@receiver(pre_save, sender=Event)
def event_creator(sender: Event, instance: Event, **kwargs: Any) -> None:
    """Single for Event."""
    if not instance.slug:
        instance.slug = unique_slug(title=instance.title)

    if instance.description:
        instance.read_time = get_read_time(words=instance.description)
