# django
from django.db.models.signals import pre_save
from django.dispatch import receiver

# app
from .models import File


@receiver(pre_save, sender=File)
def file_pre_save(sender, instance, **kwargs) -> None:  # noqa: ARG001, ANN001
    try:
        previous = File.objects.get(uuid=instance.uuid)
    except File.DoesNotExist:
        previous = None

    if not previous:
        return

    if previous.file != instance.file:
        previous.file.delete(save=False)
