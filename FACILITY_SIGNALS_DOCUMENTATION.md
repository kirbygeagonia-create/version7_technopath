# Facility Change Notifications - Django Signals Implementation

## Overview

Automatic notifications are now sent to all active users when facilities are **created**, **updated**, **deleted (soft)**, or **permanently removed (hard)** from the system.

This implementation uses Django signals to automatically trigger notifications without requiring manual intervention through the `SendNotificationView`.

## How It Works

### Signal Architecture

The facility change notification system uses three Django signals:

1. **`pre_save` signal** - Detects when a facility is being soft-deleted
2. **`post_save` signal** - Creates notifications for creation, updates, and soft-deletes
3. **`post_delete` signal** - Creates notifications for hard deletes

### Flow Diagram

```
Facility Changed
    ↓
[pre_save signal]
    ├─ Detect soft delete? → Add to tracking set
    ↓
[post_save signal]
    ├─ Is soft delete? → Create "facility_deleted" notification
    ├─ Is new facility? → Create "facility_added" notification
    └─ Is update? → Create "facility_updated" notification
         ↓
    [Create Notification]
         ↓
    [Bulk create NotificationReadStatus for all active users]
         ↓
    [Log to django.log]
```

## Notification Types

The system creates notifications with the following types:

| Type | Event | Priority | Color | Message |
|------|-------|----------|-------|---------|
| `facility_added` | New facility created | Normal (1) | Green | "A new facility 'X' (Academic Building) has been added to the campus." |
| `facility_updated` | Facility information changed | Normal (1) | Blue | "Facility 'X' information has been updated." |
| `facility_deleted` | Facility soft-deleted or hard-deleted | Important (2) | Red | "Facility 'X' has been removed from the campus." |

## Implementation Details

### Files Modified/Created

1. **`apps/notifications/models.py`**
   - Updated `TYPE_CHOICES` to include:
     - `facility_added`
     - `facility_updated`
     - `facility_deleted`

2. **`apps/facilities/apps.py`** (NEW)
   - Created `FacilitiesConfig` class
   - Imports signals in `ready()` method to ensure they're registered when Django starts

3. **`apps/facilities/__init__.py`** (UPDATED)
   - Set `default_app_config` to point to `FacilitiesConfig`

4. **`apps/facilities/signals.py`** (UPDATED)
   - Refactored to use a single, consolidated `post_save` handler
   - Added helper function `_notify_users()` for code reuse
   - Improved error handling and logging
   - Supports both soft-delete (via `is_deleted` flag) and hard-delete (via database deletion)

### Key Features

✓ **Automatic Notification Creation** - No manual API calls needed
✓ **Bulk User Notification** - All active users automatically notified via `NotificationReadStatus`
✓ **Soft-Delete Support** - Handles the soft-delete pattern used in `FacilityDetailView`
✓ **Hard-Delete Support** - Handles actual database deletions
✓ **Comprehensive Logging** - Detailed logs for debugging and monitoring
✓ **Error Handling** - Gracefully handles and logs any errors without crashing
✓ **DRY Code** - Helper functions eliminate code duplication

## Usage

### For Facility Management

No special configuration needed! The signals are automatically triggered when:

1. **Creating a Facility**
   ```python
   facility = Facility.objects.create(
       name="New Building",
       code="BLD001",
       facility_type="academic"
   )
   # → Automatically creates "facility_added" notification
   ```

2. **Updating a Facility**
   ```python
   facility.description = "Updated info"
   facility.save()
   # → Automatically creates "facility_updated" notification
   ```

3. **Soft-Deleting (via REST API)**
   ```python
   # FacilityDetailView.perform_destroy() method:
   # instance.is_deleted = True
   # instance.save()
   # → Automatically creates "facility_deleted" notification
   ```

4. **Hard-Deleting**
   ```python
   facility.delete()
   # → Automatically creates "facility_deleted" notification
   ```

### For Users

Users automatically receive notifications through the normal notification system:

1. Notifications appear in the notification feed
2. `NotificationReadStatus` is automatically created for all active users
3. Users can mark notifications as read via the `MarkOneReadView` or `MarkAllReadView` endpoints

## Configuration

### Django Settings

The signals are automatically registered when the Django app starts, provided that:

1. ✓ `'apps.facilities'` is in `INSTALLED_APPS` (already configured)
2. ✓ `FacilitiesConfig` is properly imported via `__init__.py` (already configured)

### Customization

To customize the notification behavior, edit `apps/facilities/signals.py`:

```python
# Example: Change notification priority
priority = 3  # Change from 2 to 3 for higher urgency

# Example: Change source label
source_label = "Custom Label"  # Change from "Campus Facilities"

# Example: Change source color
source_color = "purple"  # Change from auto-determined color
```

## Testing

A test script is provided to verify the signal implementation:

```bash
# Run the test script
python test_facility_signals.py
```

This script tests:
- ✓ Signal registration
- ✓ Facility creation → notification
- ✓ Facility update → notification
- ✓ Facility soft-delete → notification
- ✓ Facility hard-delete → notification (optional)

## Logging

All signal activity is logged to `django.log` with the prefix `[Facility Signal]`:

```
[Facility Signal] Created 'facility_added' notification for 'New Building' (45 users notified)
[Facility Signal] Created 'facility_updated' notification for 'New Building' (45 users notified)
[Facility Signal] Created 'facility_deleted' notification for 'Old Building' (45 users notified)
[Facility Signal] Error creating notification: [error details]
```

## Monitoring

To monitor facility change notifications in production:

```python
# View all facility notifications
from apps.notifications.models import Notification
facility_notifs = Notification.objects.filter(
    type__in=['facility_added', 'facility_updated', 'facility_deleted']
).order_by('-created_at')

# View notifications for a specific facility
facility_notifs = Notification.objects.filter(
    title__contains='Building Name'
).order_by('-created_at')

# View unread notifications for a user
from apps.notifications.models import NotificationReadStatus
unread = Notification.objects.exclude(
    notificationreadstatus__user=user
)
```

## Troubleshooting

### Issue: Notifications not being created

**Solution:**
1. Verify that `apps.facilities.apps.FacilitiesConfig` is set in `__init__.py`
2. Check that Django has started (migrations applied, server running)
3. Check `django.log` for error messages with `[Facility Signal]` prefix
4. Verify that active users exist in the database

### Issue: Duplicate notifications

**Solution:**
1. The system uses a tracking set `_soft_deleted_facilities` to prevent duplicate soft-delete notifications
2. If duplicates occur, it may indicate the post_save handler is being called twice
3. Check that there's only ONE `@receiver(post_save, sender=Facility)` decorator in `signals.py`

### Issue: Signals not imported

**Solution:**
1. Verify `apps/facilities/apps.py` exists with the correct code
2. Verify `apps/facilities/__init__.py` sets `default_app_config`
3. Restart Django server to reimport modules
4. Check server logs for import errors

## API Integration

### Existing Manual Notification Endpoint

The `SendNotificationView` (/api/notifications/send/) still works for manual notifications:

```python
POST /api/notifications/send/
{
    "title": "Manual Announcement",
    "body": "Custom message",
    "type": "announcement",
    "target": "all"
}
```

This is still useful for:
- Custom department announcements
- Emergency broadcasts
- System maintenance notices
- Non-facility related notifications

### Difference

| Feature | Automatic (Signals) | Manual (API) |
|---------|-------------------|--------------|
| Triggered by | Facility CRUD operations | API call |
| Recipient selection | All active users | Custom audience |
| Source | System | Admin/Staff user |
| Message format | Templated | Custom |
| Use case | Facility updates | Announcements |

## Performance Considerations

✓ **Bulk Operations** - Uses `bulk_create()` with `ignore_conflicts=True` for efficiency
✓ **Query Optimization** - Single query to fetch active users
✓ **Database Indexing** - Leverages existing indexes on `user.is_active` and notification foreign keys
✓ **No Blocking** - Signals run synchronously but complete quickly
✓ **Error Isolation** - Errors in notifications don't affect facility operations

## Future Enhancements

Potential improvements:

1. **Async Task Queue** - Use Celery to send notifications asynchronously
2. **Firebase Integration** - Send push notifications to mobile apps
3. **Smart Notifications** - Filter recipients based on department/role
4. **Notification Throttling** - Prevent notification spam for bulk facility imports
5. **Rich Notifications** - Include facility details (location, capacity, etc.)
6. **Email Notifications** - Send email summaries of facility changes
7. **Webhook Support** - Trigger external systems on facility changes

## References

- Django Signals Documentation: https://docs.djangoproject.com/en/4.2/topics/signals/
- Model Signals: https://docs.djangoproject.com/en/4.2/ref/signals/#model-signals
- Database-agnostic Post-save behavior: https://docs.djangoproject.com/en/4.2/ref/signals/#post_save
