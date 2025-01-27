# python
from typing import TYPE_CHECKING

# django
from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models

# app
from .notification_qs import NotificationQS

if TYPE_CHECKING:
    from ..models.notification import Notification  # noqa: F401


class NotificationManager(
    models.Manager["Notification"],
):
    # Define a default queryset for the manager.
    # This is used by self.all()
    def get_queryset(self) -> NotificationQS:
        return NotificationQS(self.model, using=self._db)

    def get_notifications(
        self, *,
        recipient: type[AbstractBaseUser],
        starred: bool | None = None,
    ) -> NotificationQS:
        qs = self.all()

        qs = qs.filter(recipient=recipient)

        # Optionally filter by starred.
        if starred:
            qs = qs.filter(starred=starred)

        qs = qs.order_by("-created")

        qs = qs.prefetch_related("recipient")
        return qs.prefetch_related("actor")


    def get_unread(
        self, *,
        recipient: type[AbstractBaseUser],
    ) -> NotificationQS:
        return (
            self.all()
            .filter(
                recipient=recipient,
                read=False,
            )
        )

    def mark_read(self, *, uuids: list[str]) -> None:
        qs = self.all().filter(uuid__in=uuids)
        qs.update(read=True)
