"""Collection of template processor."""
from typing import Any, Dict

from django.conf import settings
from rest_framework.request import Request


def from_settings(request: Request) -> Dict[str, Any]:
    """Custom template processor to show current env."""
    return {
        "ENVIRONMENT_NAME": settings.ENVIRONMENT_NAME,
        "ENVIRONMENT_COLOR": settings.ENVIRONMENT_COLOR,
    }
