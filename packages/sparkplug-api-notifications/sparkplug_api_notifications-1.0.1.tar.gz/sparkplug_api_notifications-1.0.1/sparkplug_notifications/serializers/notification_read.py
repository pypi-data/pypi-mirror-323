# python
import importlib
from typing import TYPE_CHECKING

# django
from django.conf import settings

# contrib
from rest_framework.serializers import (
    ModelSerializer,
    SlugRelatedField,
)

# app
from ..models import Notification

if TYPE_CHECKING:
    from django.contrib.auth.base_user import AbstractBaseUser


def get_class(target: str):  # noqa: ANN201
    module_name, class_name = target.rsplit(".", 1)
    module = importlib.import_module(module_name)
    return getattr(module, class_name)


UserTeaser = get_class(settings.USER_TEASER)


class NotificationRead(
    ModelSerializer["Notification"],
):
    actor_uuid: "SlugRelatedField[type[AbstractBaseUser]]" = SlugRelatedField(
        slug_field="uuid",
        source="actor",
        read_only=True,
    )

    actor = UserTeaser(read_only=True)

    class Meta:
        model = Notification

        fields = (
            "uuid",
            "created",
            "actor_uuid",
            "actor",
            "actor_text",
            "read",
            "starred",
            "message",
            "target_route",
        )

        read_only_fields = ("__all__",)
