# Requirements Document

## Introduction

This feature automates the creation of in-app notifications whenever a campus facility is added, updated, or deleted. Currently, notifications are only sent through the manual `SendNotificationView` endpoint, which requires an admin to explicitly compose and dispatch a message. The goal is to wire Django signals to the `Facility` model so that the notification pipeline is triggered automatically on every relevant change, ensuring all active users are informed of campus facility updates without manual intervention.

The existing `signals.py` file in the facilities app contains a partial implementation that references the correct models (`Notification`, `NotificationReadStatus`) but is not yet registered via an `AppConfig.ready()` hook, uses undeclared `type` values not present in `Notification.TYPE_CHOICES`, and does not handle the soft-delete pattern used by `FacilityDetailView` (`is_deleted=True` instead of a real `DELETE`). This feature formalises and completes that implementation.

---

## Glossary

- **Facility**: A campus building or location represented by the `Facility` model in `backend_django/apps/facilities/models.py`.
- **Notification**: A record in the `Notification` model (`backend_django/apps/notifications/models.py`) that carries a title, message, type, priority, and source metadata.
- **NotificationReadStatus**: A join-table record linking a `Notification` to an `AdminUser`, indicating the notification has been delivered (unread) to that user.
- **Signal_Handler**: The Django signal receiver functions defined in `backend_django/apps/facilities/signals.py`.
- **FacilitiesConfig**: The Django `AppConfig` subclass for the facilities app, responsible for registering signal handlers via its `ready()` method.
- **Soft_Delete**: The deletion pattern used by `FacilityDetailView.perform_destroy()`, which sets `Facility.is_deleted = True` and calls `save()` rather than issuing a SQL `DELETE`.
- **Active_User**: An `AdminUser` instance where `is_active=True`.
- **facility_update**: The `Notification.type` value (present in `TYPE_CHOICES`) used for facility-added and facility-updated notifications.
- **Priority_Normal**: `priority=1` — used for facility-added and facility-updated notifications.
- **Priority_Important**: `priority=2` — used for facility-deleted notifications.

---

## Requirements

### Requirement 1: Signal Registration

**User Story:** As a backend developer, I want the facility signal handlers to be automatically loaded when Django starts, so that notifications are triggered without any manual wiring per request.

#### Acceptance Criteria

1. THE `FacilitiesConfig` SHALL define a `ready()` method that imports `apps.facilities.signals`.
2. THE `FacilitiesConfig` SHALL be declared as the `default_app_config` in `backend_django/apps/facilities/__init__.py` OR set as `"default_auto_field"` via the `name` attribute so Django discovers it automatically.
3. WHEN Django starts and the facilities app is loaded, THE `Signal_Handler` SHALL be connected to `post_save` and `post_delete` signals on the `Facility` model.
4. IF the `signals` module raises an import error at startup, THEN THE `FacilitiesConfig` SHALL allow the exception to propagate so the misconfiguration is visible immediately.

---

### Requirement 2: Facility-Added Notification

**User Story:** As a campus user, I want to receive a notification when a new facility is added, so that I am aware of new buildings or locations on campus.

#### Acceptance Criteria

1. WHEN a `Facility` instance is saved with `created=True`, THE `Signal_Handler` SHALL create one `Notification` record with:
   - `title` equal to `"New Building: <facility name>"`
   - `message` equal to `"A new building '<facility name>' has been added to the campus."`
   - `type` equal to `"facility_update"`
   - `priority` equal to `1` (Normal)
   - `source_label` equal to `"Campus Updates"`
   - `source_color` equal to `"blue"`
2. WHEN the `Notification` record is created for a new facility, THE `Signal_Handler` SHALL create one `NotificationReadStatus` record for every `Active_User`, with `notification` set to the newly created `Notification`.
3. WHEN no `Active_User` records exist, THE `Signal_Handler` SHALL create the `Notification` record and skip `NotificationReadStatus` creation without raising an error.
4. IF an exception occurs during notification creation for a new facility, THEN THE `Signal_Handler` SHALL log the error at `ERROR` level and allow the `Facility` save to complete successfully.

---

### Requirement 3: Facility-Updated Notification

**User Story:** As a campus user, I want to receive a notification when an existing facility's information changes, so that I have accurate and current details about campus buildings.

#### Acceptance Criteria

1. WHEN a `Facility` instance is saved with `created=False` and `is_deleted` remains `False`, THE `Signal_Handler` SHALL create one `Notification` record with:
   - `title` equal to `"Building Updated: <facility name>"`
   - `message` equal to `"Building '<facility name>' information has been updated."`
   - `type` equal to `"facility_update"`
   - `priority` equal to `1` (Normal)
   - `source_label` equal to `"Campus Updates"`
   - `source_color` equal to `"blue"`
2. WHEN the `Notification` record is created for an updated facility, THE `Signal_Handler` SHALL create one `NotificationReadStatus` record for every `Active_User`.
3. IF an exception occurs during notification creation for an updated facility, THEN THE `Signal_Handler` SHALL log the error at `ERROR` level and allow the `Facility` save to complete successfully.

---

### Requirement 4: Facility-Deleted Notification (Soft Delete)

**User Story:** As a campus user, I want to receive a notification when a facility is removed from the campus directory, so that I know the building or location is no longer available.

#### Acceptance Criteria

1. WHEN a `Facility` instance is saved with `created=False` and `is_deleted` transitions to `True`, THE `Signal_Handler` SHALL create one `Notification` record with:
   - `title` equal to `"Building Removed: <facility name>"`
   - `message` equal to `"Building '<facility name>' has been removed from the campus."`
   - `type` equal to `"facility_update"`
   - `priority` equal to `2` (Important)
   - `source_label` equal to `"Campus Updates"`
   - `source_color` equal to `"red"`
2. WHEN the `Notification` record is created for a deleted facility, THE `Signal_Handler` SHALL create one `NotificationReadStatus` record for every `Active_User`.
3. THE `Signal_Handler` SHALL NOT create a facility-deleted notification when a `Facility` is saved with `is_deleted=False`, even if other fields change.
4. IF an exception occurs during notification creation for a deleted facility, THEN THE `Signal_Handler` SHALL log the error at `ERROR` level and allow the `Facility` save to complete successfully.

---

### Requirement 5: Notification Type Validity

**User Story:** As a backend developer, I want all automatically generated notifications to use a valid `type` value, so that the mobile client can render the correct icon and label without encountering unknown type errors.

#### Acceptance Criteria

1. THE `Signal_Handler` SHALL use only `type` values that are present in `Notification.TYPE_CHOICES` when creating `Notification` records.
2. THE `Signal_Handler` SHALL use `"facility_update"` as the `type` for all facility-change notifications (added, updated, and deleted).

---

### Requirement 6: Bulk Delivery Efficiency

**User Story:** As a backend developer, I want `NotificationReadStatus` records to be created in a single bulk operation, so that the signal handler does not issue one SQL INSERT per user and degrade performance under load.

#### Acceptance Criteria

1. WHEN creating `NotificationReadStatus` records for a notification, THE `Signal_Handler` SHALL use `NotificationReadStatus.objects.bulk_create()` with `ignore_conflicts=True`.
2. THE `Signal_Handler` SHALL fetch the list of `Active_User` records once per signal invocation and reuse it for the bulk create call.

---

### Requirement 7: Logging

**User Story:** As a backend developer, I want signal activity to be logged, so that I can audit which notifications were created automatically and diagnose failures.

#### Acceptance Criteria

1. WHEN a notification is successfully created by the `Signal_Handler`, THE `Signal_Handler` SHALL emit an `INFO`-level log message that includes the facility name and the change type (added, updated, or deleted).
2. IF an exception is caught by the `Signal_Handler`, THEN THE `Signal_Handler` SHALL emit an `ERROR`-level log message that includes the exception details.
3. THE `Signal_Handler` SHALL use a logger named `"apps.facilities.signals"` or the module-level `__name__` logger.
