"""
Django signals for Facility model.

Automatically creates notifications when facilities are:
- Created (new facility added)
- Updated (facility information changed)
- Soft-deleted (marked as inactive/removed)
- Hard-deleted (permanently removed from database)
"""

import logging
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import Facility
from apps.notifications.models import Notification, NotificationReadStatus

logger = logging.getLogger(__name__)
User = get_user_model()

# Track soft deletes to avoid duplicate notifications
_soft_deleted_facilities = set()


def _notify_users(title, message, notification_type, priority, facility_name):
    """
    Helper function to create a notification and notify all active users.
    
    Args:
        title: Notification title
        message: Notification message
        notification_type: Type of notification (e.g., 'facility_added', 'facility_updated', 'facility_deleted')
        priority: Priority level (1=normal, 2=important, 3=urgent, 4=emergency)
        facility_name: Name of the facility (for logging)
        
    Returns:
        Created Notification object or None if error occurred
    """
    try:
        # Determine source color based on notification type
        source_color = {
            'facility_deleted': 'red',
            'facility_added': 'green',
            'facility_updated': 'blue',
        }.get(notification_type, 'blue')
        
        # Create the notification
        notification = Notification.objects.create(
            title=title,
            message=message,
            type=notification_type,
            priority=priority,
            source_label="Campus Facilities",
            source_color=source_color,
            is_read=False
        )
        
        # Get all active users and create read status for each
        users = User.objects.filter(is_active=True)
        if users.exists():
            read_status_objects = [
                NotificationReadStatus(user=user, notification=notification)
                for user in users
            ]
            NotificationReadStatus.objects.bulk_create(read_status_objects, ignore_conflicts=True)
            logger.info(
                f"[Facility Signal] Created '{notification_type}' notification for '{facility_name}' "
                f"({users.count()} users notified)"
            )
        else:
            logger.warning(f"[Facility Signal] No active users found to notify for facility: {facility_name}")
        
        return notification
    
    except Exception as e:
        logger.error(f"[Facility Signal] Error creating notification: {e}", exc_info=True)
        return None


@receiver(pre_save, sender=Facility)
def detect_soft_delete(sender, instance, **kwargs):
    """
    Detect when a facility is being soft-deleted (is_deleted changes from False to True).
    
    This signal is triggered before the facility is saved, allowing us to track
    soft deletes and handle them separately in the post_save signal.
    """
    try:
        # Only proceed if this facility exists in the database
        if instance.pk is None:
            return
        
        # Get the original instance from database
        original = Facility.objects.filter(pk=instance.pk).first()
        if not original:
            return
        
        # Detect soft delete: is_deleted changes from False to True
        if not original.is_deleted and instance.is_deleted:
            _soft_deleted_facilities.add(instance.pk)
            logger.debug(f"[Facility Signal] Detected soft delete for facility: {instance.name}")
    
    except Exception as e:
        logger.error(f"[Facility Signal] Error in detect_soft_delete: {e}", exc_info=True)


@receiver(post_save, sender=Facility)
def notify_on_facility_change(sender, instance, created, **kwargs):
    """
    Automatically create notification when a facility is added, updated, or soft-deleted.
    
    Handles:
      - New facility creation (facility_added)
      - Facility updates (facility_updated)
      - Soft deletes (facility_deleted when is_deleted is set to True)
      
    Note: Hard deletes are handled by notify_facility_hard_delete signal.
    """
    try:
        # Check if this is a soft delete we detected in pre_save
        if instance.pk in _soft_deleted_facilities:
            _soft_deleted_facilities.discard(instance.pk)
            
            title = f"Facility Removed: {instance.name}"
            message = f"Facility '{instance.name}' has been removed from the campus."
            _notify_users(title, message, "facility_deleted", 2, instance.name)
            return  # Don't process as regular update
        
        # Skip notifications for deleted facilities (except soft deletes handled above)
        if instance.is_deleted:
            return
        
        # Handle new facility creation
        if created:
            title = f"New Facility: {instance.name}"
            facility_type_display = instance.get_facility_type_display()
            message = f"A new facility '{instance.name}' ({facility_type_display}) has been added to the campus."
            _notify_users(title, message, "facility_added", 1, instance.name)
        else:
            # Handle facility updates
            title = f"Facility Updated: {instance.name}"
            message = f"Facility '{instance.name}' information has been updated."
            _notify_users(title, message, "facility_updated", 1, instance.name)
        
    except Exception as e:
        logger.error(f"[Facility Signal] Error in notify_on_facility_change: {e}", exc_info=True)


@receiver(post_delete, sender=Facility)
def notify_facility_hard_delete(sender, instance, **kwargs):
    """
    Automatically create notification when a facility is hard-deleted (permanently removed from database).
    
    This signal is triggered only for hard deletes, not soft deletes.
    Soft deletes (is_deleted=True) are handled by notify_on_facility_change signal.
    """
    try:
        title = f"Facility Permanently Removed: {instance.name}"
        message = f"Facility '{instance.name}' has been permanently removed from the system."
        _notify_users(title, message, "facility_deleted", 2, instance.name)
        
    except Exception as e:
        logger.error(f"[Facility Signal] Error in notify_facility_hard_delete: {e}", exc_info=True)
