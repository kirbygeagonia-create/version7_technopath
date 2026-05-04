"""
Reset all admin account passwords to @admin123
"""
from django.core.management.base import BaseCommand
from apps.users.models import AdminUser


class Command(BaseCommand):
    help = 'Reset all admin account passwords to @admin123'

    def handle(self, *args, **options):
        password = '@admin123'
        
        usernames = [
            'safety_admin',
            'dean_seait', 'dean_agriculture', 'dean_criminology', 'dean_business',
            'dean_ict', 'dean_civil_eng', 'dean_teacher_ed', 'dean_tesda',
            'dean_gen_ed', 'dean_basic_ed',
            'head_agriculture', 'head_criminology', 'head_business', 'head_ict',
            'head_civil_eng', 'head_teacher_ed', 'head_tesda', 'head_gen_ed',
            'head_basic_ed'
        ]
        
        reset_count = 0
        
        for username in usernames:
            try:
                user = AdminUser.objects.get(username=username)
                user.set_password(password)
                user.save()
                self.stdout.write(self.style.SUCCESS(f'✅ Reset password: {username}'))
                reset_count += 1
            except AdminUser.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'❌ Not found: {username}'))
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'🎉 Reset {reset_count} account passwords to: {password}'))
