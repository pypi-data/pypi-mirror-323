# python
from typing import TYPE_CHECKING

# django
from django.db import models

# app
from .file_qs import FileQS

if TYPE_CHECKING:
    from ..models import File  # noqa: F401


class FileManager(
    models.Manager["File"],
):
    # Define a default queryset for the manager.
    # This is used by self.all()
    def get_queryset(self) -> FileQS:
        return FileQS(self.model, using=self._db)
