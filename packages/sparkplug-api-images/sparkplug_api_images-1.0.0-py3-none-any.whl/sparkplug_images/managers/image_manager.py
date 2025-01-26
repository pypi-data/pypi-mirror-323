# python
from typing import TYPE_CHECKING

# django
from django.db import models

# app
from .image_qs import ImageQS


if TYPE_CHECKING:
    from ..models.image import Image  # noqa: F401


class ImageManager(
    models.Manager["Image"],
):
    # Define a default queryset for the manager.
    # This is used by self.all()
    def get_queryset(self) -> ImageQS:
        return ImageQS(self.model, using=self._db)
