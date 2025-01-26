# python
from typing import TYPE_CHECKING

# django
from django.db.models import QuerySet


if TYPE_CHECKING:
    from ..models.image import Image  # noqa: F401


class ImageQS(
    QuerySet["Image"],
):
    """Chainable queries should be defined here."""

