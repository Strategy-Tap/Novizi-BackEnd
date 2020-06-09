"""Collection of forms."""
from typing import Any

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class AttendeeAdminForm(forms.ModelForm):
    """Custom form for Attendee."""

    def clean_events(self: "AttendeeAdminForm") -> Any:
        """Extra validation."""
        events = self.data.get("events")

        user = self.cleaned_data["user"]

        attendee = user.attendees.all()

        owner = self.cleaned_data["events"].hosted_by

        qs = attendee.filter(events=events)

        if owner == user:
            raise ValidationError(_("You are the owner of the Event"), code="invalid")

        if qs.exists():
            raise ValidationError(_("You already attended the Event"), code="invalid")

        return self.cleaned_data["events"]
