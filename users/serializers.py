"""Collection serializers."""
import re
from typing import Any, Dict

from dj_rest_auth.registration.serializers import RegisterSerializer
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, serializers

from .models import CustomUser


class ProfileSerializer(serializers.ModelSerializer):
    """Profile serializer."""

    username = serializers.CharField(required=False)

    email = serializers.EmailField(required=False)

    full_name = serializers.CharField(required=False)

    picture = serializers.ImageField(required=False)

    class Meta:
        """Meta data."""

        model = CustomUser
        fields = ("username", "email", "full_name", "picture")


class UserDetailsSerializer(serializers.Serializer):
    """User detail serializer."""

    email = serializers.EmailField(read_only=True)

    username = serializers.CharField(read_only=True)

    picture = serializers.ImageField(read_only=True)

    is_active = serializers.BooleanField(read_only=True)


class JWTSerializer(serializers.Serializer):
    """JWT serializer."""

    access_token = serializers.CharField(read_only=True)

    refresh_token = serializers.CharField(read_only=True)

    user = UserDetailsSerializer(read_only=True)


class CustomRegisterSerializer(RegisterSerializer):
    """Custom Register serializer."""

    picture = serializers.ImageField(required=False)

    full_name = serializers.CharField(max_length=300)

    phone_number = serializers.CharField(min_length=9, max_length=15, required=True)

    def get_cleaned_data(self: "CustomRegisterSerializer") -> Dict[str, Any]:
        """Cleaning for input data."""
        data_dict = super().get_cleaned_data()
        data_dict["picture"] = self.validated_data.get(
            "picture", "images/default/pic.png"
        )
        data_dict["full_name"] = self.validated_data.get("full_name", "")

        result = re.match(r"^\+?1?\d{9,15}$", self.validated_data.get("phone_number"))

        if result:
            data_dict["phone_number"] = self.validated_data.get("phone_number", "")
        else:
            raise exceptions.ParseError(
                _(
                    "Phone number must be entered in the format: '+251999999999'. "
                    "Up to 15 digits allowed."
                )
            )
        return data_dict
