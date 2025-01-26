# app
from .file_teaser import FileTeaser


class FileExpanded(
    FileTeaser,
):
    class Meta(FileTeaser.Meta):
        fields = (*FileTeaser.Meta.fields,)

        read_only_fields = ("__all__",)
