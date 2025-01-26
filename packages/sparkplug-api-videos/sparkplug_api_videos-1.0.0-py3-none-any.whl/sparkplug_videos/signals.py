# django
from django.db.models.signals import pre_save
from django.dispatch import receiver

# app
from .models import Video


@receiver(pre_save, sender=Video)
def video_pre_save(sender, instance, **kwargs) -> None:  # noqa: ARG001, ANN001
    try:
        previous = Video.objects.get(uuid=instance.uuid)
    except Video.DoesNotExist:
        previous = None

    if not previous:
        return

    if previous.file != instance.file:
        previous.file.delete(save=False)
