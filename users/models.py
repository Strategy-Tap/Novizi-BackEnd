"""Collection of model."""
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


def user_upload_to(instance: "CustomUser", filename: str) -> str:
    """A help Function to change the image upload path.

    Args:
        instance: django model
        filename: the uploaded file name

    Returns:
        path in string format
    """
    return f"images/profile_pics/{instance.username}/{filename}"


class CustomUser(AbstractUser):
    """Reference user model."""

    uuid = models.UUIDField(
        default=uuid.uuid4, editable=False, verbose_name=_("unique id")
    )

    email = models.EmailField(verbose_name=_("email address"), unique=True)

    full_name = models.CharField(verbose_name=_("full name"), max_length=300)

    picture = models.ImageField(
        verbose_name=_("picture"),
        default="images/default/pic.png",
        upload_to=user_upload_to,
    )

    class Meta:
        """Meta data."""

        verbose_name = _("profile")
        verbose_name_plural = _("profiles")

    def __str__(self: "CustomUser") -> str:
        """It return readable name for the model."""
        return f"{self.username}"
