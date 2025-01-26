# python
import logging

# contrib
from djangorestframework_camel_case.parser import (
    CamelCaseMultiPartParser,
)
from rest_framework import viewsets

# sparkplug
from sparkplug_core.views import CreateUpdateView

# app
from .. import (
    models,
    permissions,
)
from ..serializers import (
    FileTeaser,
    FileWrite,
)


log = logging.getLogger(__name__)


class File(
    CreateUpdateView,
    viewsets.GenericViewSet,
):
    model = models.File

    read_serializer_class = FileTeaser
    write_serializer_class = FileWrite

    parser_classes = (CamelCaseMultiPartParser,)
    permission_classes = (permissions.File,)

    def perform_create(self, serializer: FileWrite) -> None:
        user = self.request.user
        serializer.save(creator=user)
