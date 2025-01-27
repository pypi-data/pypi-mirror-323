# django
from django.db.models import QuerySet

# typing
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.notification import Notification  # noqa: F401


class NotificationQS(
    QuerySet["Notification"],
):
    """Chainable queries should be defined here."""

