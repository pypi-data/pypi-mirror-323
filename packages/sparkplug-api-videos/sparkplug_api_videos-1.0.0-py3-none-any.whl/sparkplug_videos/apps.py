from django.apps import AppConfig


class VideoConfig(AppConfig):
    name = "sparkplug_videos"

    def ready(self) -> None:
        from . import signals  # noqa: F401
