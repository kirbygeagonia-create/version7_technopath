"""
Management command to create all admin accounts with password @admin123
"""
from django.core.management.base import BaseCommand
from apps.users.models import AdminUser


class Command(BaseCommand):
    help = 'Create all 20 admin accounts with password @admin123'

    def handle(self, *args, **options):
        # All accounts with password @admin123
        password = '@admin123'

        admin_accounts = [
            # Super Admin
            {
                'username': 'safety_admin',
                'display_name': 'Safety and Security Admin',
                'role': 'super_admin',
                'department': 'safety_security'
            },
            # Deans
            {
                'username': 'dean_seait',
                'display_name': 'SEAIT Dean',
                'role': 'dean',
                'department': 'office_of_the_dean'
            },
            {
                'username': 'dean_agriculture',
                'display_name': 'Dean - College of Agriculture',
                'role': 'dean',
                'department': 'college_agriculture'
            },
            {
                'username': 'dean_criminology',
                'display_name': 'Dean - College of Criminology',
                'role': 'dean',
                'department': 'college_criminology'
            },
            {
                'username': 'dean_business',
                'display_name': 'Dean - College of Business',
                'role': 'dean',
                'department': 'college_business'
            },
            {
                'username': 'dean_ict',
                'display_name': 'Dean - College of ICT',
                'role': 'dean',
                'department': 'college_ict'
            },
            {
                'username': 'dean_civil_eng',
                'display_name': 'Dean - Civil Engineering',
                'role': 'dean',
                'department': 'dept_civil_engineering'
            },
            {
                'username': 'dean_teacher_ed',
                'display_name': 'Dean - Teacher Education',
                'role': 'dean',
                'department': 'college_teacher_education'
            },
            {
                'username': 'dean_tesda',
                'display_name': 'Dean - TESDA',
                'role': 'dean',
                'department': 'tesda'
            },
            {
                'username': 'dean_gen_ed',
                'display_name': 'Dean - General Education',
                'role': 'dean',
                'department': 'general_education'
            },
            {
                'username': 'dean_basic_ed',
                'display_name': 'Dean - Basic Education',
                'role': 'dean',
                'department': 'basic_education'
            },
            # Program Heads
            {
                'username': 'head_agriculture',
                'display_name': 'Program Head - Agriculture',
                'role': 'program_head',
                'department': 'college_agriculture'
            },
            {
                'username': 'head_criminology',
                'display_name': 'Program Head - Criminology',
                'role': 'program_head',
                'department': 'college_criminology'
            },
            {
                'username': 'head_business',
                'display_name': 'Program Head - Business',
                'role': 'program_head',
                'department': 'college_business'
            },
            {
                'username': 'head_ict',
                'display_name': 'Program Head - ICT',
                'role': 'program_head',
                'department': 'college_ict'
            },
            {
                'username': 'head_civil_eng',
                'display_name': 'Program Head - Civil Engineering',
                'role': 'program_head',
                'department': 'dept_civil_engineering'
            },
            {
                'username': 'head_teacher_ed',
                'display_name': 'Program Head - Teacher Education',
                'role': 'program_head',
                'department': 'college_teacher_education'
            },
            {
                'username': 'head_tesda',
                'display_name': 'Program Head - TESDA',
                'role': 'program_head',
                'department': 'tesda'
            },
            {
                'username': 'head_gen_ed',
                'display_name': 'Program Head - General Education',
                'role': 'program_head',
                'department': 'general_education'
            },
            # Basic Ed Head
            {
                'username': 'head_basic_ed',
                'display_name': 'Basic Ed Head - Basic Education',
                'role': 'basic_ed_head',
                'department': 'basic_education'
            },
        ]

        created_count = 0
        skipped_count = 0

        for account in admin_accounts:
            username = account['username']

            # Check if user already exists
            if AdminUser.objects.filter(username=username).exists():
                self.stdout.write(self.style.WARNING(f'Skipped (exists): {username}'))
                skipped_count += 1
                continue

            try:
                user = AdminUser.objects.create_user(
                    username=username,
                    password=password,
                    display_name=account['display_name'],
                    role=account['role'],
                    department=account['department'],
                    is_active=True
                )
                self.stdout.write(self.style.SUCCESS(f'Created: {username} ({account["role"]} - {account["department"]})'))
                created_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating {username}: {e}'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'✅ Complete! Created {created_count} accounts, skipped {skipped_count} existing accounts.'))
        self.stdout.write(self.style.NOTICE(f'🔑 All passwords set to: {password}'))
