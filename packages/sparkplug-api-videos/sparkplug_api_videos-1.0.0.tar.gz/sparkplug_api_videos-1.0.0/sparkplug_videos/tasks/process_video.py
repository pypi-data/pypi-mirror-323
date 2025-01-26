# python
import logging
from pathlib import Path

# django
from django.core.files import File

# contrib
from decouple import config
from huey.contrib.djhuey import task

# app
from .. import (
    models,
    services,
)


log = logging.getLogger(__name__)


@task()
def process_video(video_uuid: str) -> None:
    try:
        instance = models.Video.objects.get(uuid=video_uuid)
    except models.Video.DoesNotExist:
        return

    if bool(instance.file) is False:
        return

    log.debug(
        "process video",
        extra={ video_uuid: instance.uuid},
    )

    environment = config("API_ENV")
    source = instance.file.path if environment == "dev" else instance.file.url

    filepath = services.optimize_video(
        source=source,
        filename=instance.uuid,
    )

    try:
        with Path.open(filepath, "rb") as f:
            file = File(f)
            filename = Path(filepath).name

            if instance.file:
                instance.file.delete()

            instance.file.save(filename, file)

    except FileNotFoundError:
        log.exception(
            "Failed to optimize video",
            extra={ video_uuid: instance.uuid },
        )
