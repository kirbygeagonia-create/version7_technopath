from django.db import models


class Announcement(models.Model):

    STATUS_CHOICES = [
        ('pending_approval', 'Pending Approval'),
        ('published',        'Published'),
        ('rejected',         'Rejected'),
        ('archived',         'Archived'),
    ]

    SCOPE_CHOICES = [
        ('campus_wide',       'Entire Campus (all users)'),
        ('all_college',       'All College Students'),
        ('basic_ed_only',     'Basic Education Only'),
        ('department',        'Specific Department Only'),
        ('specific_users',    'Specific Users (by name)'),
    ]

    # Content
    title             = models.CharField(max_length=200)
    content           = models.TextField()

    # Authorship
    # Edge case (Task B): If the Dean/admin is deactivated or hard deleted, 
    # what happens to their live announcements? 
    # Fallback: Since on_delete=SET_NULL, the announcement remains live regardless.
    # The source_label and source_color are captured below at creation time
    # so the frontend will still render the card correctly even if created_by is null.
    created_by        = models.ForeignKey(
        'users.AdminUser', on_delete=models.SET_NULL,
        null=True, related_name='created_announcements'
    )

    # Label shown to mobile users — stored at creation time so it persists
    # even if the admin account is later renamed or deleted
    source_label      = models.CharField(
        max_length=200,
        help_text='Department label shown on the mobile notification card'
    )
    source_color      = models.CharField(
        max_length=20, default='orange',
        help_text='Color key for the department chip on mobile'
    )

    # Scope
    scope             = models.CharField(max_length=20, choices=SCOPE_CHOICES, default='campus_wide')
    target_department = models.CharField(
        max_length=50, blank=True, null=True,
        help_text='Set when scope=department to filter which users see this'
    )
    target_users = models.JSONField(
        default=list, blank=True,
        help_text='List of user IDs/names when scope=specific_users. Format: ["user1", "user2"]'
    )

    # Approval workflow
    status            = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_approval')
    requires_approval = models.BooleanField(default=True)

    approved_by       = models.ForeignKey(
        'users.AdminUser', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='approved_announcements'
    )
    rejected_by       = models.ForeignKey(
        'users.AdminUser', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='rejected_announcements'
    )
    rejection_note    = models.TextField(
        blank=True, null=True,
        help_text='Reason for rejection — shown to the submitting admin'
    )
    approved_at       = models.DateTimeField(blank=True, null=True)

    # Archive tracking
    archived_by       = models.ForeignKey(
        'users.AdminUser', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='archived_announcements'
    )
    archived_at       = models.DateTimeField(blank=True, null=True)

    # Soft delete
    is_deleted        = models.BooleanField(default=False)
    
    def is_visible_to(self, user):
        """Check if this announcement should be visible to a given user"""
        if self.status != 'published' or self.is_deleted:
            return False
        if self.scope == 'campus_wide':
            return True
        if self.scope == 'all_college':
            return getattr(user, 'role', None) == 'college_student'
        if self.scope == 'basic_ed_only':
            return getattr(user, 'role', None) == 'basic_ed_student'
        if self.scope == 'department':
            return getattr(user, 'department', None) == self.target_department
        if self.scope == 'specific_users':
            # Check by user ID or username
            user_id = str(getattr(user, 'id', ''))
            username = getattr(user, 'username', '') or getattr(user, 'email', '')
            targets = [str(t).lower() for t in (self.target_users or [])]
            return user_id.lower() in targets or username.lower() in targets
        return False

    # Timestamps
    created_at        = models.DateTimeField(auto_now_add=True)
    updated_at        = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'announcements'
        ordering = ['-created_at']

    def publish(self, approved_by_user):
        """Approve and publish. Automatically creates a mobile Notification."""
        from django.utils import timezone
        from apps.notifications.models import Notification

        self.status      = 'published'
        self.approved_by = approved_by_user
        self.approved_at = timezone.now()
        self.save()

        # Format scope for visibility
        display_label = self.source_label
        if self.scope == 'campus_wide':
            display_label = f"Campus-Wide • {display_label}"
        elif self.scope == 'all_college':
            display_label = f"College • {display_label}"
        elif self.scope == 'basic_ed_only':
            display_label = f"Basic Ed • {display_label}"

        Notification.objects.create(
            title        = self.title,
            message      = self.content,
            type         = 'announcement',
            source_label = display_label,
            source_color = self.source_color,
            announcement = self,
            created_by   = approved_by_user,
        )

    def reject(self, rejected_by_user, note=''):
        """Reject with optional note to the submitter."""
        self.status       = 'rejected'
        self.rejected_by  = rejected_by_user
        self.rejection_note = note
        self.save()

    def archive(self, archived_by_user=None):
        """Archive a published announcement (soft delete from public view)."""
        from django.utils import timezone
        self.status = 'archived'
        self.archived_at = timezone.now()
        self.archived_by = archived_by_user
        self.save()

    def __str__(self):
        return f'[{self.status.upper()}] {self.title} — {self.source_label}'
