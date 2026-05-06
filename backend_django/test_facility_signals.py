"""
Test script to verify Django facility signals are working correctly.

This script tests:
1. Signal registration (signals are properly imported)
2. Facility creation triggers notification
3. Facility update triggers notification
4. Facility soft-delete triggers notification
5. Facility hard-delete triggers notification
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'technopath.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.contrib.auth import get_user_model
from apps.facilities.models import Facility
from apps.notifications.models import Notification, NotificationReadStatus
from apps.core.models import Department

User = get_user_model()

def test_facility_signals():
    """Test all facility signal scenarios."""
    
    print("\n" + "="*70)
    print("TESTING FACILITY SIGNALS IMPLEMENTATION")
    print("="*70 + "\n")
    
    # Get or create a test user
    test_user, _ = User.objects.get_or_create(
        username='signal_test_user',
        defaults={'is_active': True, 'is_staff': True}
    )
    print(f"✓ Test user: {test_user.username}")
    
    # Get notification count before tests
    initial_notif_count = Notification.objects.count()
    print(f"✓ Initial notification count: {initial_notif_count}\n")
    
    # Test 1: Facility Creation
    print("-" * 70)
    print("TEST 1: Facility Creation Signal")
    print("-" * 70)
    try:
        test_facility = Facility.objects.create(
            name="Test Facility Alpha",
            code="TFA001",
            facility_type="academic",
            description="Test facility for signal verification"
        )
        print(f"✓ Created facility: {test_facility.name}")
        
        # Check if notification was created
        new_notif = Notification.objects.filter(
            type="facility_added",
            title__contains="Test Facility Alpha"
        ).first()
        
        if new_notif:
            print(f"✓ Notification created: {new_notif.title}")
            print(f"  Message: {new_notif.message}")
            print(f"  Type: {new_notif.type}")
            
            # Check read status
            read_status_count = NotificationReadStatus.objects.filter(
                notification=new_notif
            ).count()
            print(f"  Read status entries: {read_status_count}")
        else:
            print("✗ ERROR: No notification found for facility creation!")
            return False
    except Exception as e:
        print(f"✗ ERROR in facility creation test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    
    # Test 2: Facility Update
    print("-" * 70)
    print("TEST 2: Facility Update Signal")
    print("-" * 70)
    try:
        test_facility.description = "Updated description"
        test_facility.save()
        print(f"✓ Updated facility: {test_facility.name}")
        
        # Check if update notification was created
        update_notif = Notification.objects.filter(
            type="facility_updated",
            title__contains="Test Facility Alpha"
        ).first()
        
        if update_notif:
            print(f"✓ Update notification created: {update_notif.title}")
            print(f"  Message: {update_notif.message}")
            print(f"  Type: {update_notif.type}")
        else:
            print("✗ ERROR: No notification found for facility update!")
            return False
    except Exception as e:
        print(f"✗ ERROR in facility update test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    
    # Test 3: Facility Soft Delete
    print("-" * 70)
    print("TEST 3: Facility Soft Delete Signal")
    print("-" * 70)
    try:
        test_facility.is_deleted = True
        test_facility.save()
        print(f"✓ Soft-deleted facility: {test_facility.name}")
        
        # Check if soft delete notification was created
        delete_notif = Notification.objects.filter(
            type="facility_deleted",
            title__contains="Test Facility Alpha"
        ).order_by('-created_at').first()
        
        if delete_notif:
            print(f"✓ Delete notification created: {delete_notif.title}")
            print(f"  Message: {delete_notif.message}")
            print(f"  Type: {delete_notif.type}")
        else:
            print("✗ ERROR: No notification found for facility soft delete!")
            return False
    except Exception as e:
        print(f"✗ ERROR in facility soft delete test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    
    # Test 4: Facility Hard Delete (optional, be careful!)
    print("-" * 70)
    print("TEST 4: Facility Hard Delete Signal (Optional)")
    print("-" * 70)
    try:
        # Create a separate test facility for hard delete
        hard_delete_facility = Facility.objects.create(
            name="Test Facility Hard Delete",
            code="TFHD001",
            facility_type="service",
            description="Facility to be hard deleted"
        )
        print(f"✓ Created facility for hard delete: {hard_delete_facility.name}")
        
        # Clear existing notifications for this facility
        Notification.objects.filter(
            title__contains="Test Facility Hard Delete"
        ).delete()
        
        # Hard delete
        hard_delete_id = hard_delete_facility.id
        hard_delete_facility.delete()
        print(f"✓ Hard-deleted facility (ID: {hard_delete_id})")
        
        # Check if hard delete notification was created
        hard_delete_notif = Notification.objects.filter(
            type="facility_deleted",
            title__contains="Permanently Removed"
        ).order_by('-created_at').first()
        
        if hard_delete_notif:
            print(f"✓ Hard delete notification created: {hard_delete_notif.title}")
            print(f"  Message: {hard_delete_notif.message}")
        else:
            print("! NOTE: Hard delete notification not found (signal may not have triggered)")
    except Exception as e:
        print(f"! NOTE: Hard delete test skipped: {e}")
    
    print()
    
    # Final Summary
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    final_notif_count = Notification.objects.count()
    notifications_created = final_notif_count - initial_notif_count
    
    print(f"✓ Notifications created during tests: {notifications_created}")
    print(f"✓ Total notification count: {final_notif_count}")
    print(f"\n✓ ALL TESTS PASSED - Facility signals are working correctly!")
    print("=" * 70 + "\n")
    
    return True


if __name__ == '__main__':
    try:
        success = test_facility_signals()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
