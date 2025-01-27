# python
import logging
from typing import Any

# django
from django.contrib.auth import get_user_model

# contrib
from huey.contrib.djhuey import db_task

# sparkplug
from sparkplug_core.utils import (
    send_client_action,
    send_admin_action,
)

# app
from . import (
    enums,
    models,
    serializers,
)


log = logging.getLogger(__name__)


@db_task()
def send_notification(  # noqa: PLR0913
    *,
    recipient_uuid: str,
    message: str,
    actor_uuid: str | None = None,
    actor_text: str = "",
    target_route: Any = None,  # noqa: ANN401
    target_actor: bool = False,
) -> None:
    actor = None

    try:
        recipient = get_user_model().admins_and_users.get(
            uuid=recipient_uuid,
        )

        if actor_uuid is not None:
            actor = get_user_model().admins_and_users.get(
                uuid=actor_uuid,
            )

            if target_actor:
                target_route = actor.get_route()

    except get_user_model().DoesNotExist as e:
        log.exception("User not found - sending notification", exc_info=e)
        return

    notification = models.Notification.objects.create(
        recipient_id=recipient.id,
        actor=actor,
        actor_text=actor_text,
        message=message,
        target_route=target_route,
    )

    serializer = serializers.NotificationRead(
        instance=notification,
    )

    if recipient.is_staff:
        send_admin_action(
            action_type=enums.NotificationAction.INSERT,
            payload={
                "data": serializer.data,
            },
        )


    else:
        send_client_action(
            target_uuid=recipient_uuid,
            action_type=enums.NotificationAction.INSERT,
            payload={
                "data": serializer.data,
            },
        )
