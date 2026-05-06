"""
Django signals for Room model.
Automatically creates user notifications when rooms are added, updated, or removed.
"""
import logging

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Room
from apps.notifications.models import Notification

logger = logging.getLogger(__name__)
_soft_deleted_rooms = set()


def _notify_room(title, message):
    try:
        Notification.objects.create(
            title=title,
            message=message,
            type='room_update',
            source_label='Campus Facilities',
            source_color='blue',
            priority=1,
            is_read=False,
        )
        logger.info('[Room Signal] Notification created: %s', title)
    except Exception as e:
        logger.error('[Room Signal] Failed to create notification: %s', e, exc_info=True)


@receiver(pre_save, sender=Room)
def detect_room_soft_delete(sender, instance, **kwargs):
    if instance.pk is None:
        return
    try:
        original = Room.objects.filter(pk=instance.pk).first()
        if original and not original.is_deleted and instance.is_deleted:
            _soft_deleted_rooms.add(instance.pk)
    except Exception as e:
        logger.error('[Room Signal] pre_save error: %s', e)


@receiver(post_save, sender=Room)
def notify_on_room_change(sender, instance, created, **kwargs):
    try:
        facility_name = 'Unknown Building'
        try:
            facility_name = instance.facility.name
        except Exception:
            pass

        if instance.pk in _soft_deleted_rooms:
            _soft_deleted_rooms.discard(instance.pk)
            _notify_room(
                f'Room Removed: {instance.name}',
                f'Room "{instance.name}" in {facility_name} has been removed from the system.'
            )
            return

        if instance.is_deleted:
            return

        if created:
            _notify_room(
                f'New Room: {instance.name}',
                f'Room "{instance.name}" (Floor {instance.floor}) in {facility_name} is now available.'
            )
        else:
            _notify_room(
                f'Room Updated: {instance.name}',
                f'Room "{instance.name}" in {facility_name} has been updated.'
            )
    except Exception as e:
        logger.error('[Room Signal] post_save error: %s', e, exc_info=True)
