"""Collection of forms."""
from typing import Any

from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.core.exceptions import ValidationError

from .models import CustomUser
from .validators import (
    validate_confusables,
    validate_confusables_email,
    validate_reserved_name,
)


class UserAdminForm(forms.ModelForm):
    """Custom form for users form in admin page."""

    def clean_username(self: "UserAdminForm") -> Any:
        """Extra validation for username."""
        username = self.data.get("username")

        validate_confusables(value=username, exception_class=ValidationError)

        validate_reserved_name(value=username, exception_class=ValidationError)

        return self.cleaned_data["username"]

    def clean_email(self: "UserAdminForm") -> Any:
        """Extra validation for email."""
        email = self.data.get("email")

        local_part, domain = self.data.get("email")

        validate_confusables_email(
            local_part=local_part, domain=domain, exception_class=ValidationError
        )

        validate_reserved_name(value=email, exception_class=ValidationError)

        return self.cleaned_data["email"]


class CustomUserCreationForm(UserCreationForm):
    """Custom form for users creation form in admin page."""

    class Meta:
        """Meta data."""

        model = CustomUser
        fields = ("username", "password")


class CustomUserChangeForm(UserChangeForm):
    """Custom form for users change form in admin page."""

    class Meta:
        """Meta data."""

        model = CustomUser
        fields = ("username", "email")
