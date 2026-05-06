import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Path
from apps.notifications.models import Notification

logger = logging.getLogger(__name__)


def _notify_navigation_change(message):
    try:
        Notification.objects.create(
            title='Navigation Route Updated',
            message=message,
            type='info',
            source_label='Campus Navigation',
            source_color='teal',
            priority=1,
        )
    except Exception as e:
        logger.error('[Path Signal] %s', e)


@receiver(post_save, sender=Path)
def notify_path_change(sender, instance, created, **kwargs):
    if instance.is_deleted:
        return
    if created:
        _notify_navigation_change('A new walking route has been added on campus. Tap Navigate to use it.')
    else:
        _notify_navigation_change('A campus walking route was updated. Open Navigate to refresh your route options.')


@receiver(post_delete, sender=Path)
def notify_path_delete(sender, instance, **kwargs):
    _notify_navigation_change('A campus walking route was removed. Navigate now shows the latest available routes.')
