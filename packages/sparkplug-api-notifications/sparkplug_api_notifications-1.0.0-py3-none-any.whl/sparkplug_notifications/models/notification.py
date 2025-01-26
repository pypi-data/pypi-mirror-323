# python
from typing import ClassVar

# django
from django.conf import settings
from django.db import models

# contrib
from psqlextra.types import PostgresPartitioningMethod
from psqlextra.models import PostgresPartitionedModel

# sparkplug
from sparkplug_core.models import BaseModel

# app
from .. import managers


class Notification(
    PostgresPartitionedModel,
    BaseModel,
):
    # Owner
    # notifications >-- user
    recipient = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    read = models.BooleanField(
        default=False,
    )

    starred = models.BooleanField(
        default=False,
    )

    # notifications >-- user
    actor = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
    )

    actor_text = models.CharField(
        max_length=255,
    )

    message = models.CharField(
        max_length=255,
    )

    target_route = models.JSONField(
        null=True,
    )

    objects = managers.NotificationManager()

    class Meta:
        indexes = (models.Index(fields=["uuid"]),)
        ordering = ("-created",)

    class PartitioningMeta:
        method = PostgresPartitioningMethod.RANGE
        key: ClassVar = ["created"]

    def __str__(self) -> str:
        return f"{self.recipient} - {self.message}"
