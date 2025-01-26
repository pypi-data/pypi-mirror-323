# python
from typing import TYPE_CHECKING

# django
from django.db.models import QuerySet

if TYPE_CHECKING:
    from ..models.video import Video  # noqa: F401


class VideoQS(
    QuerySet["Video"],
):
    """Chainable queries should be defined here."""

