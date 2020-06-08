"""Collection django-allauth adapter."""
from typing import Any

from allauth.account.adapter import DefaultAccountAdapter
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request

from .validators import (
    validate_confusables,
    validate_confusables_email,
    validate_reserved_name,
)


class CustomAccountAdapter(DefaultAccountAdapter):
    """Custom account adapter."""

    def clean_username(
        self: "CustomAccountAdapter", username: str, shallow: bool = False
    ) -> str:
        """Extra validation for username.

        Args:
            username: Username to check.
            shallow: bool field.

        Returns:
            username if it valid or raise exception

        Raises:
            ValidationError If username is not valid.
        """
        username = super().clean_username(username, shallow)

        validate_reserved_name(value=username, exception_class=ValidationError)

        validate_confusables(value=username, exception_class=ValidationError)

        return username

    def clean_email(self: "CustomAccountAdapter", email: str) -> str:
        """Extra validation for email.

        Args:
            email: Email to check.

        Returns:
            email if it valid or raise exception

        Raises:
            ValidationError If email is not valid.
        """
        email = super().clean_email(email)
        local_part, domain = email.split("@")

        validate_reserved_name(value=local_part, exception_class=ValidationError)

        validate_confusables_email(
            local_part=local_part, domain=domain, exception_class=ValidationError,
        )

        return email

    def save_user(
        self: "CustomAccountAdapter",
        request: Request,
        user: Any,
        form: Any,
        commit: bool = False,
    ) -> Any:
        """Extra validation for email.

        Args:
            request: Request object
            user: ?
            form: ?
            commit: bool field to indicted when to commit.

        Returns:
            user object
        """
        user = super().save_user(request, user, form, commit)

        data = form.cleaned_data

        user.phone_number = data.get("phone_number")

        user.full_name = data.get("full_name")

        user.picture = data.get("picture")

        user.save()

        return user
