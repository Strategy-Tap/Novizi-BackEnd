"""Core app for users app."""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    """Class representing a Django application and its configuration."""

    name = "users"
    verbose_name = _("Users")
