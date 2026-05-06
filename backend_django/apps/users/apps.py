from django.apps import AppConfig
from django.db import connection
import os
import sys


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    verbose_name = 'Users'

    def ready(self):
        # Skip during management commands that don't need DB at app load time
        # (collectstatic, migrate, shell, etc.)
        skip_commands = {'collectstatic', 'migrate', 'makemigrations', 'shell',
                         'dbshell', 'check', 'showmigrations', 'sqlmigrate',
                         'seed_bulk_campus', 'seed_default_data'}
        if sys.argv and len(sys.argv) > 1 and sys.argv[1] in skip_commands:
            return

        import threading
        def delayed_setup():
            import time
            # Retry loop — wait for DB to be reachable (internal hostname
            # resolves only after the service is fully started on Render)
            for attempt in range(12):  # try for up to 60 seconds
                time.sleep(5)
                try:
                    from django.db import connection
                    connection.ensure_connection()
                    connection.close()
                    break  # DB is reachable
                except Exception:
                    if attempt == 11:
                        print("❌ DB never became reachable — skipping admin setup")
                        return
                    continue
            self.setup_admin_accounts()

        threading.Thread(target=delayed_setup, daemon=True).start()
    
    def setup_admin_accounts(self):
        """Create missing admin accounts and reset all passwords"""
        from apps.users.models import AdminUser
        
        # Full admin data with roles and departments
        ADMIN_DATA = [
            {'username': 'safety_admin', 'role': 'super_admin', 'department': 'safety_security', 
             'display_name': 'Safety and Security Office', 'is_staff': True, 'is_superuser': True},
            {'username': 'dean_seait', 'role': 'dean', 'department': 'office_of_the_dean',
             'display_name': 'Office of the Dean', 'is_staff': True},
            {'username': 'dean_agriculture', 'role': 'dean', 'department': 'college_agriculture',
             'display_name': 'Dean — College of Agriculture and Fisheries', 'is_staff': True},
            {'username': 'dean_criminology', 'role': 'dean', 'department': 'college_criminology',
             'display_name': 'Dean — College of Criminal Justice Education', 'is_staff': True},
            {'username': 'dean_business', 'role': 'dean', 'department': 'college_business',
             'display_name': 'Dean — College of Business and Good Governance', 'is_staff': True},
            {'username': 'dean_ict', 'role': 'dean', 'department': 'college_ict',
             'display_name': 'Dean — College of Information and Communication Technology', 'is_staff': True},
            {'username': 'dean_civil_eng', 'role': 'dean', 'department': 'dept_civil_engineering',
             'display_name': 'Dean — Department of Civil Engineering', 'is_staff': True},
            {'username': 'dean_teacher_ed', 'role': 'dean', 'department': 'college_teacher_education',
             'display_name': 'Dean — College of Teacher Education', 'is_staff': True},
            {'username': 'dean_tesda', 'role': 'dean', 'department': 'tesda',
             'display_name': 'Dean — TESDA', 'is_staff': True},
            {'username': 'dean_gen_ed', 'role': 'dean', 'department': 'general_education',
             'display_name': 'Dean — General Education Department', 'is_staff': True},
            {'username': 'dean_basic_ed', 'role': 'dean', 'department': 'basic_education',
             'display_name': 'Dean — Basic Education', 'is_staff': True},
            {'username': 'head_agriculture', 'role': 'program_head', 'department': 'college_agriculture',
             'display_name': 'Program Head — Agriculture', 'is_staff': True},
            {'username': 'head_criminology', 'role': 'program_head', 'department': 'college_criminology',
             'display_name': 'Program Head — Criminology', 'is_staff': True},
            {'username': 'head_business', 'role': 'program_head', 'department': 'college_business',
             'display_name': 'Program Head — Business', 'is_staff': True},
            {'username': 'head_ict', 'role': 'program_head', 'department': 'college_ict',
             'display_name': 'Program Head — ICT', 'is_staff': True},
            {'username': 'head_civil_eng', 'role': 'program_head', 'department': 'dept_civil_engineering',
             'display_name': 'Program Head — Civil Engineering', 'is_staff': True},
            {'username': 'head_teacher_ed', 'role': 'program_head', 'department': 'college_teacher_education',
             'display_name': 'Program Head — Teacher Education', 'is_staff': True},
            {'username': 'head_tesda', 'role': 'program_head', 'department': 'tesda',
             'display_name': 'TESDA Coordinator', 'is_staff': True},
            {'username': 'head_gen_ed', 'role': 'program_head', 'department': 'general_education',
             'display_name': 'Program Head — General Education', 'is_staff': True},
            {'username': 'head_basic_ed', 'role': 'basic_ed_head', 'department': 'basic_education',
             'display_name': 'Head — Basic Education', 'is_staff': True},
        ]
        
        password = '@admin123'
        created = 0
        updated = 0
        
        try:
            for admin in ADMIN_DATA:
                # Make a copy to avoid mutating original
                admin_data = admin.copy()
                username = admin_data.pop('username')
                is_superuser = admin_data.pop('is_superuser', False)
                
                try:
                    user = AdminUser.objects.get(username=username)
                    # Update password
                    user.set_password(password)
                    user.save()
                    updated += 1
                except AdminUser.DoesNotExist:
                    # Create new user
                    user = AdminUser.objects.create_user(
                        username=username,
                        password=password,
                        **admin_data
                    )
                    if is_superuser:
                        user.is_superuser = True
                        user.save()
                    created += 1
            
            print(f"\n{'='*50}")
            print(f"✅ ADMIN ACCOUNTS SETUP COMPLETE")
            print(f"   Created: {created} | Updated: {updated}")
            print(f"   All passwords: {password}")
            print(f"{'='*50}\n")
        except Exception as e:
            print(f"❌ Error setting up admin accounts: {e}")
