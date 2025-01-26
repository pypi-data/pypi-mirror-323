# python
from typing import TYPE_CHECKING

# django
from django.db.models import QuerySet

if TYPE_CHECKING:
    from ..models.file import File  # noqa: F401


class FileQS(
    QuerySet["File"],
):
    """Chainable queries should be defined here."""

