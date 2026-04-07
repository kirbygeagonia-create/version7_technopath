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
    map_svg_id = models.CharField(max_length=100, blank=True, null=True)
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
