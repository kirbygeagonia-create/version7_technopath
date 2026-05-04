from django.apps import AppConfig
from django.db import connection
import os


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    verbose_name = 'Users'

    def ready(self):
        # Only run in production (PostgreSQL) and not during migrations
        if 'RENDER' in os.environ or 'postgresql' in os.environ.get('DATABASE_URL', ''):
            try:
                # Check if users table exists
                with connection.cursor() as cursor:
                    cursor.execute("SELECT to_regclass('users_adminuser')")
                    if cursor.fetchone()[0]:
                        self.auto_reset_passwords()
            except:
                pass  # Table doesn't exist yet (migrations not run)
    
    def auto_reset_passwords(self):
        """Auto-reset all admin passwords on startup"""
        from apps.users.models import AdminUser
        
        password = '@admin123'
        usernames = [
            'safety_admin', 'dean_seait', 'dean_agriculture', 'dean_criminology',
            'dean_business', 'dean_ict', 'dean_civil_eng', 'dean_teacher_ed',
            'dean_tesda', 'dean_gen_ed', 'dean_basic_ed', 'head_agriculture',
            'head_criminology', 'head_business', 'head_ict', 'head_civil_eng',
            'head_teacher_ed', 'head_tesda', 'head_gen_ed', 'head_basic_ed'
        ]
        
        updated = 0
        for username in usernames:
            try:
                user = AdminUser.objects.get(username=username)
                user.set_password(password)
                user.save()
                updated += 1
            except AdminUser.DoesNotExist:
                pass
        
        if updated > 0:
            print(f"✅ Auto-reset {updated} admin passwords to: {password}")
