# contrib
from rest_framework.serializers import ModelSerializer

# app
from ..models import File


class FileWrite(
    ModelSerializer["File"],
):
    class Meta:
        model = File

        fields = (
            "file",
        )
