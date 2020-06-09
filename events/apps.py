"""Core app for events app."""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class EventsConfig(AppConfig):
    """Class representing a Django application and its configuration."""

    name = "events"
    verbose_name = _("Events")
