"""Admin module for users app."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from import_export import resources
from import_export.admin import ExportActionModelAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import CustomUser


class UserResource(resources.ModelResource):
    """ModelResource is Resource subclass for handling Django models."""

    class Meta:
        """Meta data."""

        model = CustomUser
        fields = ("username", "email", "date_joined", "last_login")

        export_order = ("username", "email", "date_joined", "last_login")


@admin.register(CustomUser)
class CustomUserAdmin(ExportActionModelAdmin, UserAdmin):
    """Configure the users app in admin page."""

    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    resource_class = UserResource
    model = CustomUser
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2",),
            },
        ),
        (_("Permissions"), {"fields": ("is_superuser", "is_staff")}),
    )

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Personal info"),
            {"classes": ("collapse",), "fields": ("full_name", "email", "picture",)},
        ),
        (
            _("Permissions"),
            {
                "classes": ("collapse",),
                "fields": (
                    "is_active",
                    "is_superuser",
                    "is_staff",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            _("Important dates"),
            {"classes": ("collapse",), "fields": ("last_login", "date_joined")},
        ),
    )

    list_display = (
        "username",
        "email",
        "is_active",
    )

    list_filter = ("last_login",)

    date_hierarchy = "date_joined"


admin.site.site_title = _("Novizi site admin")
admin.site.site_header = _("Novizi Dashboard")
admin.site.index_title = _("Welcome to Novizi")
