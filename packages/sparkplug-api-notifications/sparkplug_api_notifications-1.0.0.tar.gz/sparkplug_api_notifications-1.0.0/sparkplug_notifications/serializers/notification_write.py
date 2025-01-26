# contrib
from rest_framework.serializers import ModelSerializer

# app
from ..models import Notification


class NotificationWrite(
    ModelSerializer["Notification"],
):
    class Meta:
        model = Notification

        fields = (
            "starred",
        )
