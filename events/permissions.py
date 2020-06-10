"""Collection permissions."""
from typing import Any

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

        return obj.hosted_by == request.user


class IsProposerOrReadOnly(permissions.BasePermission):
    """Allows full access to object owner otherwise read only."""

    def has_object_permission(
        self: "IsProposerOrReadOnly", request: Request, view: Any, obj: Any
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

        return obj.proposed_by == request.user
