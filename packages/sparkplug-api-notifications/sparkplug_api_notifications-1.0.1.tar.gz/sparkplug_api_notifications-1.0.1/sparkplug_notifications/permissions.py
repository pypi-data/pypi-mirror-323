# django
from django.views import View

# contrib
from rest_framework.request import Request

# sparkplug
from sparkplug_core.permissions import (
    ActionPermission,
    IsAuthenticated,
)

# app
from .models import Notification


class IsOwner(IsAuthenticated):
    def has_object_permission(
        self,
        request: Request,
        view: View,  # noqa: ARG002
        obj: Notification,
    ) -> bool:
        return obj.recipient == request.user


class Permissions(
    ActionPermission,
):
    # object permissions
    read_perms = IsOwner
    write_perms = IsOwner
