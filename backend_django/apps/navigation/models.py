from django.db import models
from apps.facilities.models import Facility
from apps.rooms.models import Room

class NavigationNode(models.Model):
    NODE_TYPES = [
        ('room', 'Room'), ('facility', 'Facility'), ('waypoint', 'Waypoint'),
        ('entrance', 'Entrance'), ('staircase', 'Staircase'),
        ('elevator', 'Elevator'), ('junction', 'Junction'),
    ]
    name = models.CharField(max_length=200)
    node_type = models.CharField(max_length=20, choices=NODE_TYPES)
    facility = models.ForeignKey(Facility, on_delete=models.SET_NULL, null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    map_svg_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    x = models.FloatField()
    y = models.FloatField()
    floor = models.IntegerField(default=1)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'navigation_nodes'

    def __str__(self):
        return f'{self.name} ({self.node_type})'

class NavigationEdge(models.Model):
    from_node = models.ForeignKey(NavigationNode, on_delete=models.CASCADE, related_name='edges_from')
    to_node = models.ForeignKey(NavigationNode, on_delete=models.CASCADE, related_name='edges_to')
    distance = models.IntegerField()
    is_bidirectional = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'navigation_edges'

    def __str__(self):
        return f'{self.from_node.name} → {self.to_node.name} ({self.distance})'


class Path(models.Model):
    """User-created navigation paths with multiple stops."""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    facility = models.ForeignKey(Facility, on_delete=models.SET_NULL, null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    floor = models.IntegerField(default=1)
    created_by = models.ForeignKey('users.AdminUser', on_delete=models.SET_NULL, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'navigation_paths'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def from_location(self):
        """Get the starting point of the path."""
        first_point = self.points.filter(is_deleted=False).order_by('sequence').first()
        return first_point.element_id if first_point else ''

    @property
    def to_location(self):
        """Get the destination of the path."""
        last_point = self.points.filter(is_deleted=False).order_by('sequence').last()
        return last_point.element_id if last_point else ''


class PathPoint(models.Model):
    """Individual stop points within a path."""
    path = models.ForeignKey(Path, on_delete=models.CASCADE, related_name='points')
    sequence = models.IntegerField()
    element_id = models.CharField(max_length=100)
    x = models.FloatField(default=0)
    y = models.FloatField(default=0)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'navigation_path_points'
        ordering = ['sequence']

    def __str__(self):
        return f'{self.path.name} - Stop {self.sequence}: {self.element_id}'
