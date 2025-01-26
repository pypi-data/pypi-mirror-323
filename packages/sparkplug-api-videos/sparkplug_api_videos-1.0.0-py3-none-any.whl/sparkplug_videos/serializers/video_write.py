# django
from django.core.validators import FileExtensionValidator

# contrib
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

# app
from .. import models


class VideoWrite(
    ModelSerializer[models.Video],
):
    file = serializers.FileField(
        validators=[
            FileExtensionValidator(
                allowed_extensions=["mp4", "mov", "webm"],
            ),
        ],
    )

    class Meta:
        model = models.Video

        fields = (
            "file",
        )
