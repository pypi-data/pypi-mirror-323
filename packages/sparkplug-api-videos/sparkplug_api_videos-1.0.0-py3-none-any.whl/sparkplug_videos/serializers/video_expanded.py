# app
from .video_teaser import VideoTeaser


class VideoExpanded(
    VideoTeaser,
):
    class Meta(VideoTeaser.Meta):
        fields = (*VideoTeaser.Meta.fields,)

        read_only_fields = ("__all__",)
