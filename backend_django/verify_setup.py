#!/usr/bin/env python
"""
Django Setup Verification Script for TechnoPath
Run this after creating the virtual environment and installing requirements
"""

import os
import sys

# Add the backend_django directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_django_installation():
    """Verify Django and required packages are installed"""
    try:
        import django
        print(f"✓ Django {django.VERSION} installed")
        
        import rest_framework
        print("✓ Django REST Framework installed")
        
        import rest_framework_simplejwt
        print("✓ Django REST Framework SimpleJWT installed")
        
        import corsheaders
        print("✓ Django CORS Headers installed")
        
        import decouple
        print("✓ Python Decouple installed")
        
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("\nPlease run: pip install -r requirements.txt")
        return False

def check_settings():
    """Verify Django settings are valid"""
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'technopath.settings')
        import django
        django.setup()
        
        from django.conf import settings
        
        # Check critical settings
        checks = [
            ('SECRET_KEY', settings.SECRET_KEY != 'django-insecure-technopath-seait-dev-key-change-in-production'),
            ('INSTALLED_APPS', len(settings.INSTALLED_APPS) >= 10),
            ('DATABASES', 'default' in settings.DATABASES),
            ('REST_FRAMEWORK', 'DEFAULT_AUTHENTICATION_CLASSES' in settings.REST_FRAMEWORK),
        ]
        
        for name, passed in checks:
            status = "✓" if passed else "✗"
            print(f"{status} {name} configured")
        
        return all(passed for _, passed in checks)
    except Exception as e:
        print(f"✗ Settings error: {e}")
        return False

def check_models():
    """Verify all app models can be imported"""
    try:
        from apps.users.models import AdminUser
        print("✓ Users models")
        
        from apps.facilities.models import Facility
        print("✓ Facilities models")
        
        from apps.rooms.models import Room
        print("✓ Rooms models")
        
        from apps.navigation.models import NavigationNode, NavigationEdge
        print("✓ Navigation models")
        
        from apps.chatbot.models import FAQEntry, AIChatLog
        print("✓ Chatbot models")
        
        from apps.notifications.models import Notification
        print("✓ Notifications models")
        
        from apps.feedback.models import Feedback
        print("✓ Feedback models")
        
        return True
    except Exception as e:
        print(f"✗ Models error: {e}")
        return False

def run_django_check():
    """Run Django system check command"""
    try:
        from django.core.management import call_command
        from io import StringIO
        
        out = StringIO()
        call_command('check', stdout=out, stderr=out)
        output = out.getvalue()
        
        if 'no issues' in output.lower() or output.strip() == '':
            print("✓ Django system check passed")
            return True
        else:
            print(f"! Django check output: {output}")
            return True  # Still return True as warnings are OK
    except Exception as e:
        print(f"✗ Django check failed: {e}")
        return False

def check_migrations():
    """Check if migrations are needed"""
    try:
        from django.core.management import call_command
        from io import StringIO
        
        out = StringIO()
        call_command('showmigrations', '--plan', stdout=out)
        output = out.getvalue()
        
        # Check if any migrations are shown as [ ] (not applied)
        if '[ ]' in output:
            print("! Migrations needed - run: python manage.py migrate")
            return False
        else:
            print("✓ All migrations applied")
            return True
    except Exception as e:
        print(f"! Could not check migrations: {e}")
        return False

def main():
    """Run all verification checks"""
    print("=" * 60)
    print("TechnoPath Django Setup Verification")
    print("=" * 60)
    
    results = []
    
    print("\n[1/5] Checking Django installation...")
    results.append(check_django_installation())
    
    print("\n[2/5] Checking Django settings...")
    results.append(check_settings())
    
    print("\n[3/5] Checking models...")
    results.append(check_models())
    
    print("\n[4/5] Running Django system check...")
    results.append(run_django_check())
    
    print("\n[5/5] Checking migrations...")
    results.append(check_migrations())
    
    print("\n" + "=" * 60)
    if all(results):
        print("✓ All checks passed! Django is ready to run.")
        print("\nStart the server with:")
        print("  python manage.py runserver")
    else:
        print("✗ Some checks failed. Please fix the issues above.")
    print("=" * 60)
    
    return 0 if all(results) else 1

if __name__ == '__main__':
    sys.exit(main())
