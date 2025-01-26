# python
from typing import TYPE_CHECKING

# django
from django.conf import settings

# contrib
from decouple import config
from rest_framework.serializers import (
    ModelSerializer,
    SerializerMethodField,
    SlugRelatedField,
)

# app
from .. import models

if TYPE_CHECKING:
    from django.contrib.auth.base_user import AbstractBaseUser


class FileTeaser(
    ModelSerializer["models.File"],
):
    creator_uuid: "SlugRelatedField[type[AbstractBaseUser]]" = SlugRelatedField(
        slug_field="uuid",
        source="creator",
        read_only=True,
    )

    file = SerializerMethodField()

    class Meta:
        model = models.File

        fields = (
            "uuid",
            "created",
            "creator_uuid",
            "file",
        )

        read_only_fields = ("__all__",)

    def get_file(self, obj: models.File) -> str:
        if not obj.file:
            return ""

        environment = config("API_ENV")
        file_url = obj.file.url
        if environment == "dev":
            file_url = f"{settings.API_URL}{obj.file.url}"

        return file_url
