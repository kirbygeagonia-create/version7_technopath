#!/usr/bin/env python
"""Quick test to verify admin login credentials."""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'technopath.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from apps.users.models import AdminUser

print("Testing admin login...")
print("-" * 50)

# Test super admin
username = "safety_admin"
password = "123"

try:
    user = AdminUser.objects.get(username=username)
    print(f"Username: {username}")
    print(f"Is active: {user.is_active}")
    print(f"Login attempts: {user.login_attempts}")
    print(f"Locked until: {user.locked_until}")
    print(f"Role: {user.role}")
    
    # Test password
    if user.check_password(password):
        print("✅ Password is CORRECT")
    else:
        print("❌ Password is WRONG")
        
    if user.is_locked():
        print("⚠️  Account is LOCKED")
    else:
        print("✅ Account is NOT locked")
        
except AdminUser.DoesNotExist:
    print(f"❌ User '{username}' not found!")
    print("\nAvailable users:")
    for u in AdminUser.objects.all()[:5]:
        print(f"  - {u.username}")
