"""Collection permissions."""
from typing import Any

from django.utils.translation import gettext_lazy as _
from rest_framework import permissions
from rest_framework.request import Request


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Allows full access to object owner otherwise read only."""

    def has_object_permission(
        self: "IsOwnerOrReadOnly", request: Request, view: Any, obj: Any
    ) -> bool:
        """Checking if user have object level permission.

        Args:
            request: Request object
            view: Any type of view
            obj: Any django model

        Returns:
            If user is owner of the object it return True otherwise it false
        """
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj == request.user


class IsNotAuthenticated(permissions.BasePermission):
    """Allows access only to unauthenticated users."""

    message = _("You are authenticated.")

    def has_permission(self: "IsNotAuthenticated", request: Request, view: Any) -> bool:
        """Check if user is anonymous.

        Args:
            request: Request object
            view: Any type of view

        Returns:
            If user is anonymous it return True otherwise it false
        """
        return not bool(request.user and request.user.is_authenticated)
