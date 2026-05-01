from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsSuperAdmin(BasePermission):
    message = 'Only the Safety and Security Office (Super Admin) can perform this action.'
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'super_admin'


class IsDeanOrSuperAdmin(BasePermission):
    message = 'Only the Dean or Super Admin can perform this action.'
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ('super_admin', 'dean')


class ReadOnlyOrSuperAdmin(BasePermission):
    """
    Public read access (GET, HEAD, OPTIONS) for everyone.
    Write access (POST, PUT, PATCH, DELETE) restricted to Super Admin only.
    Used for: Facilities, Navigation nodes/edges, FAQ entries, Map markers/labels.
    """
    message = 'Only the Super Admin can modify this resource.'

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role == 'super_admin'


class CanManageRoom(BasePermission):
    """
    Read access: public (any user can list/view rooms).
    Write access:
      - Super Admin → all rooms
      - Dean / Program Head / Basic Ed Head → only rooms in facilities
        linked to their department (via facility.department)

    NOTE: For create (POST), the facility FK is checked from request data.
    For update/delete, the room's existing facility.department is checked.
    """
    message = 'You can only manage rooms within your department.'

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        if request.user.role == 'super_admin':
            return True
        # Non-super admins must have a department and one of the room-managing roles
        return (
            request.user.role in ('dean', 'program_head', 'basic_ed_head')
            and request.user.department
        )

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.user.role == 'super_admin':
            return True
        user_dept = request.user.department
        if not user_dept:
            return False
        if not hasattr(obj, 'facility') or not obj.facility:
            return False
        facility_dept = obj.facility.department
        if not facility_dept:
            return False
        # Exact case-insensitive match.
        # AdminUser.department stores the raw code string set at account creation
        # (e.g. 'college_ict'). Department.code stores the same value.
        # A substring check was fragile ('it' matching 'college_ict' unintentionally).
        return (facility_dept.code or '').lower() == user_dept.lower()


class CanApproveAnnouncements(BasePermission):
    """Only Super Admin can approve announcements. Dean has no approval authority."""
    message = 'Only the Super Admin can approve announcements.'
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'super_admin'


class CanPostAnnouncement(BasePermission):
    message = 'Admin login required to post announcements.'
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.can_post_announcement()


class IsAnyAdmin(BasePermission):
    message = 'Admin login required.'
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in (
            'super_admin', 'dean', 'program_head', 'basic_ed_head'
        )


class CanViewAuditLog(BasePermission):
    """Only Super Admin can view full audit log. Dean has no audit log access."""
    message = 'Only the Super Admin can view the audit log.'
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == 'super_admin'
        )
