# python
import logging

# contrib
from djangorestframework_camel_case.parser import CamelCaseMultiPartParser
from rest_framework import viewsets

# sparkplug
from sparkplug_core.views import CreateUpdateView

# app
from .. import (
    models,
    permissions,
    tasks,
)
from ..serializers import (
    VideoTeaser,
    VideoWrite,
)


log = logging.getLogger(__name__)


class Video(
    CreateUpdateView,
    viewsets.GenericViewSet,
):
    model = models.Video

    read_serializer_class = VideoTeaser
    write_serializer_class = VideoWrite

    parser_classes = (CamelCaseMultiPartParser,)
    permission_classes = (permissions.Video,)

    def perform_create(self, serializer: VideoWrite) -> None:
        user = self.request.user
        instance = serializer.save(creator=user)
        tasks.process_video(instance.uuid)()

    def perform_update(self, serializer: VideoWrite) -> None:
        instance = serializer.save()
        tasks.process_video(instance.uuid)()
