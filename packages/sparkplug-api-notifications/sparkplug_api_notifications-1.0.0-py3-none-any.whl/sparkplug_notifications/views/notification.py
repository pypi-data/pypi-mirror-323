# python
import logging

# contrib
from django.db.models import QuerySet
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

# sparkplug
from sparkplug_core.utils import get_bool
from sparkplug_core.views import BaseView

# app
from .. import (
    models,
    permissions,
)
from ..serializers import (
    NotificationRead,
    NotificationWrite,
)


log = logging.getLogger(__name__)


class Notification(
    BaseView,
    mixins.UpdateModelMixin,
    viewsets.ReadOnlyModelViewSet,
):
    model = models.Notification

    read_serializer_class = NotificationRead
    write_serializer_class = NotificationWrite

    permission_classes = (permissions.Permissions,)

    def get_list_queryset(self) -> QuerySet[models.Notification]:
        user = self.request.user

        starred = None
        str_starred = self.request.query_params.get("starred", None)
        if str_starred:
            starred = get_bool(str_starred)

        return self.model.objects.get_notifications(
            recipient=user,
            starred=starred,
        )

    @action(detail=False, methods=["put"])
    def read(self, request: Request) -> Response:
        """Retrieve the list of notifications by uuids and mark them as read."""
        self.model.objects.mark_read(
            uuids=request.data,
        )

        return Response(status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["get"],
        url_path="unread-count",
    )
    def unread_count(self, request: Request) -> Response:
        """Retrieve the user's count of unread notifications."""
        unread = self.model.objects.get_unread(
            recipient=request.user,
        )

        return Response(
            status=status.HTTP_200_OK,
            data=unread.count(),
        )
