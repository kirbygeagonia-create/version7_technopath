import json
from django.utils import timezone
from django.db import models
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as http_status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import AdminUser
from .permissions import IsSuperAdmin, IsAnyAdmin


def write_audit(admin, action, entity_type=None, entity_id=None,
                entity_label=None, old_val=None, new_val=None, request=None):
    """Write a row to AdminAuditLog. Import here to avoid circular imports."""
    try:
        from apps.core.models import AdminAuditLog
        ip = None
        if request:
            x_fwd = request.META.get('HTTP_X_FORWARDED_FOR')
            ip = x_fwd.split(',')[0].strip() if x_fwd else request.META.get('REMOTE_ADDR')
        AdminAuditLog.objects.create(
            admin=admin, action=action,
            entity_type=entity_type, entity_id=entity_id, entity_label=entity_label,
            old_value_json=json.dumps(old_val)  if old_val  else None,
            new_value_json=json.dumps(new_val)  if new_val  else None,
            ip_address=ip,
        )
    except Exception:
        pass  # Audit log failure must never crash the main request


class LoginView(APIView):
    permission_classes = []

    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')

        if not username or not password:
            return Response(
                {'error': 'Username and password are required.'},
                status=http_status.HTTP_400_BAD_REQUEST
            )

        try:
            user = AdminUser.objects.get(username=username, is_active=True)
        except AdminUser.DoesNotExist:
            return Response(
                {'error': 'Invalid username or password.'},
                status=http_status.HTTP_401_UNAUTHORIZED
            )

        if user.is_locked():
            mins = max(1, int((user.locked_until - timezone.now()).total_seconds() / 60) + 1)
            return Response(
                {'error': f'This account is temporarily locked. Try again in {mins} minute(s).'},
                status=http_status.HTTP_403_FORBIDDEN
            )

        if not user.check_password(password):
            user.record_failed_login()
            left = max(0, 5 - user.login_attempts)
            if left > 0:
                msg = f'Invalid username or password. {left} attempt(s) remaining before lockout.'
            else:
                msg = 'Account locked for 30 minutes due to too many failed attempts.'
            return Response({'error': msg}, status=http_status.HTTP_401_UNAUTHORIZED)

        user.record_successful_login()
        write_audit(user, 'login', 'user', user.id,
                    user.display_name or user.username, request=request)

        refresh = RefreshToken.for_user(user)
        return Response({
            'access':  str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id':               user.id,
                'username':         user.username,
                'display_name':     user.display_name or user.username,
                'role':             user.role,
                'role_label':       user.get_role_display(),
                'department':       user.department,
                'department_label': user.get_department_label(),
                'department_color': user.get_department_color(),
                **user.get_permissions_dict(),
            }
        })


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        write_audit(request.user, 'logout', 'user', request.user.id,
                    request.user.display_name or request.user.username, request=request)
        return Response({'message': 'Logged out.'})


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        u = request.user
        return Response({
            'id':               u.id,
            'username':         u.username,
            'display_name':     u.display_name or u.username,
            'role':             u.role,
            'role_label':       u.get_role_display(),
            'department':       u.department,
            'department_label': u.get_department_label(),
            'department_color': u.get_department_color(),
            **u.get_permissions_dict(),
        })


class AdminListCreateView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        # Allow Super Admin to include inactive accounts via query param (Q3 fix)
        include_inactive = request.query_params.get('include_inactive') == 'true'
        queryset = AdminUser.objects.all() if include_inactive else AdminUser.objects.filter(is_active=True)
        users = queryset.order_by('role', 'department')
        return Response([{
            'id':               u.id,
            'username':         u.username,
            'display_name':     u.display_name,
            'role':             u.role,
            'role_label':       u.get_role_display(),
            'department':       u.department,
            'department_label': u.get_department_label(),
            'last_login':       u.last_login,
            'created_at':       u.created_at,
        } for u in users])

    def post(self, request):
        d = request.data
        for field in ['username', 'password', 'role', 'department']:
            if not d.get(field):
                return Response({'error': f'"{field}" is required.'},
                                status=http_status.HTTP_400_BAD_REQUEST)
        if AdminUser.objects.filter(username=d['username']).exists():
            return Response({'error': 'That username already exists.'},
                            status=http_status.HTTP_400_BAD_REQUEST)
        if d['role'] == 'dean' and d['department']:
            if AdminUser.objects.filter(role='dean', department=d['department']).exists():
                return Response({'error': f"A Dean account already exists for that department."},
                                status=http_status.HTTP_400_BAD_REQUEST)
        user = AdminUser.objects.create_user(
            username      = d['username'],
            password      = d['password'],
            role          = d['role'],
            department    = d['department'],
            display_name  = d.get('display_name', ''),
            department_label = d.get('department_label', ''),
            email         = d.get('email', ''),
            is_staff      = True,
        )
        write_audit(request.user, 'create', 'admin_user', user.id, user.username,
                    new_val={'username': user.username, 'role': user.role,
                             'department': user.department}, request=request)
        return Response({'id': user.id, 'username': user.username},
                        status=http_status.HTTP_201_CREATED)


class AdminDetailView(APIView):
    permission_classes = [IsSuperAdmin]

    def put(self, request, pk):
        try:
            user = AdminUser.objects.get(pk=pk)
        except AdminUser.DoesNotExist:
            return Response({'error': 'Admin not found.'}, status=404)

        old = {'role': user.role, 'department': user.department}
        user.display_name     = request.data.get('display_name', user.display_name)
        user.role             = request.data.get('role', user.role)
        user.department       = request.data.get('department', user.department)
        
        if user.role == 'dean' and user.department:
            if AdminUser.objects.filter(role='dean', department=user.department).exclude(pk=user.pk).exists():
                return Response({'error': f"A Dean account already exists for that department."},
                                status=http_status.HTTP_400_BAD_REQUEST)

        user.department_label = request.data.get('department_label', user.department_label)
        user.email            = request.data.get('email', user.email)
        if request.data.get('password'):
            user.set_password(request.data['password'])
            write_audit(request.user, 'reset_password', 'admin_user',
                        user.id, user.username, request=request)
        user.save()
        write_audit(request.user, 'update', 'admin_user', user.id, user.username,
                    old_val=old,
                    new_val={'role': user.role, 'department': user.department},
                    request=request)
        return Response({'message': 'Admin account updated.'})

    def delete(self, request, pk):
        try:
            user = AdminUser.objects.get(pk=pk)
        except AdminUser.DoesNotExist:
            return Response({'error': 'Admin not found.'}, status=404)
        if user.role == 'super_admin':
            return Response({'error': 'The Super Admin account cannot be deactivated.'},
                            status=http_status.HTTP_403_FORBIDDEN)
        user.is_active = False
        user.save()
        write_audit(request.user, 'soft_delete', 'admin_user',
                    user.id, user.username, request=request)
        return Response({'message': f'Account for {user.username} deactivated.'})


class AuditLogView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.can_view_audit_log():
            return Response({'error': 'Access denied.'}, status=403)
        from apps.core.models import AdminAuditLog
        qs = AdminAuditLog.objects.select_related('admin').order_by('-created_at')
        if request.query_params.get('entity_type'):
            qs = qs.filter(entity_type=request.query_params['entity_type'])
        if request.query_params.get('action'):
            qs = qs.filter(action=request.query_params['action'])
        qs = qs[:300]
        return Response([{
            'id':           l.id,
            'admin':        l.admin.display_name if l.admin else 'Unknown',
            'department':   l.admin.get_department_label() if l.admin else '',
            'action':       l.action,
            'entity_type':  l.entity_type,
            'entity_id':    l.entity_id,
            'entity_label': l.entity_label,
            'ip_address':   l.ip_address,
            'created_at':   l.created_at,
        } for l in qs])


class PublicDirectoryView(APIView):
    """Public endpoint for instructor and employee directory - no authentication required"""
    permission_classes = []

    def get(self, request):
        """Return list of instructors and employees for public directory"""
        # Get admin users who are instructors or program heads (visible to public)
        from .models import AdminUser
        
        # Filter for roles that should be visible in public directory
        visible_roles = ['dean', 'program_head', 'basic_ed_head']
        
        users = AdminUser.objects.filter(
            role__in=visible_roles,
            is_active=True
        ).order_by('display_name')
        
        data = [{
            'id': user.id,
            'name': user.display_name or user.username,
            'department': user.get_department_label(),
            'role': user.get_role_display(),
            'email': user.email if user.show_email_public else None,
            'office': user.office_location or None,
        } for user in users]
        
        return Response(data)


class UserListView(APIView):
    """List all admin users for admin dashboard with optional search."""
    permission_classes = [IsAnyAdmin]

    def get(self, request):
        users = AdminUser.objects.all().order_by('-created_at')
        
        # Search by username or display_name
        search = request.query_params.get('search', '').strip().lower()
        if search:
            users = users.filter(
                models.Q(username__icontains=search) | 
                models.Q(display_name__icontains=search)
            )
        
        # Limit results for performance
        limit = min(int(request.query_params.get('limit', 50)), 100)
        users = users[:limit]
        
        data = [{
            'id': user.id,
            'username': user.username,
            'display_name': user.display_name,
            'email': user.email,
            'role': user.role,
            'department': user.department,
            'is_active': user.is_active,
            'is_superuser': user.is_superuser,
            'created_at': user.created_at.isoformat() if user.created_at else None,
        } for user in users]
        return Response(data)
