# python
from typing import TYPE_CHECKING

# django
from django.db import models

# app
from .video_qs import VideoQS

if TYPE_CHECKING:
    from ..models import Video  # noqa: F401


class VideoManager(
    models.Manager["Video"],
):
    # Define a default queryset for the manager.
    # This is used by self.all()
    def get_queryset(self) -> VideoQS:
        return VideoQS(self.model, using=self._db)
