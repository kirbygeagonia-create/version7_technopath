# Technopath Database Relationship Cardinality and Comments

## Table: `django_admin_log`

**django_admin_log** -> **admin_users**
- **Cardinality**: `1..* <-> 1:1`
- **Field**: User
- **Comment**: Multiple django_admin_log can belong to one admin_users. A admin_users contains zero or more django_admin_log.

**django_admin_log** -> **django_content_type**
- **Cardinality**: `0..* <-> 0:1`
- **Field**: Content type
- **Comment**: Multiple django_admin_log can belong to one django_content_type. A django_content_type contains zero or more django_admin_log.

## Table: `auth_permission`

**auth_permission** -> **django_content_type**
- **Cardinality**: `1..* <-> 1:1`
- **Field**: Content type
- **Comment**: Multiple auth_permission can belong to one django_content_type. A django_content_type contains zero or more auth_permission.

## Table: `auth_group_permissions`

**auth_group_permissions** -> **auth_group**
- **Cardinality**: `1..* <-> 1:1`
- **Field**: Group
- **Comment**: Multiple auth_group_permissions can belong to one auth_group. A auth_group contains zero or more auth_group_permissions.

**auth_group_permissions** -> **auth_permission**
- **Cardinality**: `1..* <-> 1:1`
- **Field**: Permission
- **Comment**: Multiple auth_group_permissions can belong to one auth_permission. A auth_permission contains zero or more auth_group_permissions.

## Table: `admin_users_groups`

**admin_users_groups** -> **admin_users**
- **Cardinality**: `1..* <-> 1:1`
- **Field**: Adminuser
- **Comment**: Multiple admin_users_groups can belong to one admin_users. A admin_users contains zero or more admin_users_groups.

**admin_users_groups** -> **auth_group**
- **Cardinality**: `1..* <-> 1:1`
- **Field**: Group
- **Comment**: Multiple admin_users_groups can belong to one auth_group. A auth_group contains zero or more admin_users_groups.

## Table: `admin_users_user_permissions`

**admin_users_user_permissions** -> **admin_users**
- **Cardinality**: `1..* <-> 1:1`
- **Field**: Adminuser
- **Comment**: Multiple admin_users_user_permissions can belong to one admin_users. A admin_users contains zero or more admin_users_user_permissions.

**admin_users_user_permissions** -> **auth_permission**
- **Cardinality**: `1..* <-> 1:1`
- **Field**: Permission
- **Comment**: Multiple admin_users_user_permissions can belong to one auth_permission. A auth_permission contains zero or more admin_users_user_permissions.

## Table: `facilities`

**facilities** -> **departments**
- **Cardinality**: `0..* <-> 0:1`
- **Field**: Department
- **Comment**: Multiple facilities can belong to one departments. A departments contains zero or more facilities.

## Table: `rooms`

**rooms** -> **facilities**
- **Cardinality**: `1..* <-> 1:1`
- **Field**: Facility
- **Comment**: Multiple rooms can belong to one facilities. A facilities contains zero or more rooms.

## Table: `navigation_nodes`

**navigation_nodes** -> **facilities**
- **Cardinality**: `0..* <-> 0:1`
- **Field**: Facility
- **Comment**: Multiple navigation_nodes can belong to one facilities. A facilities contains zero or more navigation_nodes.

**navigation_nodes** -> **rooms**
- **Cardinality**: `0..* <-> 0:1`
- **Field**: Room
- **Comment**: Multiple navigation_nodes can belong to one rooms. A rooms contains zero or more navigation_nodes.

## Table: `navigation_edges`

**navigation_edges** -> **navigation_nodes**
- **Cardinality**: `1..* <-> 1:1`
- **Field**: From node
- **Comment**: Multiple navigation_edges can belong to one navigation_nodes. A navigation_nodes contains zero or more navigation_edges.

**navigation_edges** -> **navigation_nodes**
- **Cardinality**: `1..* <-> 1:1`
- **Field**: To node
- **Comment**: Multiple navigation_edges can belong to one navigation_nodes. A navigation_nodes contains zero or more navigation_edges.

## Table: `ai_chat_logs`

**ai_chat_logs** -> **faq_entries**
- **Cardinality**: `0..* <-> 0:1`
- **Field**: Faq entry
- **Comment**: Multiple ai_chat_logs can belong to one faq_entries. A faq_entries contains zero or more ai_chat_logs.

## Table: `notifications`

**notifications** -> **announcements**
- **Cardinality**: `0..* <-> 0:1`
- **Field**: Announcement
- **Comment**: Multiple notifications can belong to one announcements. A announcements contains zero or more notifications.

**notifications** -> **admin_users**
- **Cardinality**: `0..* <-> 0:1`
- **Field**: Created by
- **Comment**: Multiple notifications can belong to one admin_users. A admin_users contains zero or more notifications.

## Table: `notification_read_status`

**notification_read_status** -> **admin_users**
- **Cardinality**: `1..* <-> 1:1`
- **Field**: User
- **Comment**: Multiple notification_read_status can belong to one admin_users. A admin_users contains zero or more notification_read_status.

**notification_read_status** -> **notifications**
- **Cardinality**: `1..* <-> 1:1`
- **Field**: Notification
- **Comment**: Multiple notification_read_status can belong to one notifications. A notifications contains zero or more notification_read_status.

## Table: `feedback`

**feedback** -> **facilities**
- **Cardinality**: `0..* <-> 0:1`
- **Field**: Facility
- **Comment**: Multiple feedback can belong to one facilities. A facilities contains zero or more feedback.

**feedback** -> **rooms**
- **Cardinality**: `0..* <-> 0:1`
- **Field**: Room
- **Comment**: Multiple feedback can belong to one rooms. A rooms contains zero or more feedback.

## Table: `departments`

**departments** -> **admin_users**
- **Cardinality**: `0..* <-> 0:1`
- **Field**: Head user
- **Comment**: Multiple departments can belong to one admin_users. A admin_users contains zero or more departments.

## Table: `map_markers`

**map_markers** -> **facilities**
- **Cardinality**: `0..* <-> 0:1`
- **Field**: Facility
- **Comment**: Multiple map_markers can belong to one facilities. A facilities contains zero or more map_markers.

**map_markers** -> **rooms**
- **Cardinality**: `0..* <-> 0:1`
- **Field**: Room
- **Comment**: Multiple map_markers can belong to one rooms. A rooms contains zero or more map_markers.

## Table: `notification_preferences`

**notification_preferences** -> **admin_users**
- **Cardinality**: `1..* <-> 1:1`
- **Field**: User
- **Comment**: Multiple notification_preferences can belong to one admin_users. A admin_users contains zero or more notification_preferences.

**notification_preferences** -> **notification_types**
- **Cardinality**: `1..* <-> 1:1`
- **Field**: Notification type
- **Comment**: Multiple notification_preferences can belong to one notification_types. A notification_types contains zero or more notification_preferences.

## Table: `admin_audit_log`

**admin_audit_log** -> **admin_users**
- **Cardinality**: `0..* <-> 0:1`
- **Field**: Admin
- **Comment**: Multiple admin_audit_log can belong to one admin_users. A admin_users contains zero or more admin_audit_log.

## Table: `search_history`

**search_history** -> **admin_users**
- **Cardinality**: `0..* <-> 0:1`
- **Field**: User
- **Comment**: Multiple search_history can belong to one admin_users. A admin_users contains zero or more search_history.

## Table: `app_config`

**app_config** -> **admin_users**
- **Cardinality**: `0..* <-> 0:1`
- **Field**: Updated by
- **Comment**: Multiple app_config can belong to one admin_users. A admin_users contains zero or more app_config.

## Table: `announcements`

**announcements** -> **admin_users**
- **Cardinality**: `0..* <-> 0:1`
- **Field**: Created by
- **Comment**: Multiple announcements can belong to one admin_users. A admin_users contains zero or more announcements.

**announcements** -> **admin_users**
- **Cardinality**: `0..* <-> 0:1`
- **Field**: Approved by
- **Comment**: Multiple announcements can belong to one admin_users. A admin_users contains zero or more announcements.

**announcements** -> **admin_users**
- **Cardinality**: `0..* <-> 0:1`
- **Field**: Rejected by
- **Comment**: Multiple announcements can belong to one admin_users. A admin_users contains zero or more announcements.

**announcements** -> **admin_users**
- **Cardinality**: `0..* <-> 0:1`
- **Field**: Archived by
- **Comment**: Multiple announcements can belong to one admin_users. A admin_users contains zero or more announcements.

