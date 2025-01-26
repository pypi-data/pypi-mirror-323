# django
from django.conf import settings
from django.db import models

# sparkplug
from sparkplug_core.models import BaseModel

# app
from .. import (
    managers,
    uploads,
)


class Video(
    BaseModel,
):
    creator = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="+",
    )

    file = models.FileField(
        upload_to=uploads.file_location,
        null=True,
    )

    objects = managers.VideoManager()

    class Meta:
        indexes = (models.Index(fields=["uuid"]),)

    def __str__(self) -> str:
        return self.uuid

    def delete(self, *args, **kwargs) -> None:
        self.file.delete()
        super().delete(*args, **kwargs)
