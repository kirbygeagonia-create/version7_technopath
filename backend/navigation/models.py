from django.db import models
import json

class NavigationNode(models.Model):
    """Represents a location/building on the map"""
    id = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=200)
    node_type = models.CharField(max_length=50, choices=[
        ('building', 'Building'),
        ('room', 'Room'),
        ('facility', 'Facility'),
        ('entrance', 'Entrance'),
        ('landmark', 'Landmark'),
    ], default='building')
    x = models.FloatField(help_text='X coordinate (0-1 normalized)')
    y = models.FloatField(help_text='Y coordinate (0-1 normalized)')
    building = models.CharField(max_length=100, blank=True, null=True)
    floor = models.IntegerField(default=1)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'navigation_nodes'
        ordering = ['name']

    def __str__(self):
        return self.name


class SvgPath(models.Model):
    """Represents a navigable path between two points"""
    id = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    # New format: from/to building IDs
    from_node = models.ForeignKey(NavigationNode, on_delete=models.CASCADE, 
                                   related_name='paths_from', null=True, blank=True)
    to_node = models.ForeignKey(NavigationNode, on_delete=models.CASCADE,
                                 related_name='paths_to', null=True, blank=True)
    
    # Path points stored as JSON array of [x, y] coordinates
    points = models.JSONField(default=list, help_text='Array of [x, y] coordinate pairs')
    
    # Legacy support
    element_ids = models.JSONField(default=list, blank=True, 
                                    help_text='Legacy: array of SVG element IDs')
    
    distance = models.FloatField(default=0, help_text='Path distance in meters')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'svg_paths'
        ordering = ['-updated_at']

    def __str__(self):
        return self.name

    def calculate_distance(self):
        """Calculate total path distance from points"""
        total = 0
        pts = self.points
        for i in range(len(pts) - 1):
            dx = pts[i+1][0] - pts[i][0]
            dy = pts[i+1][1] - pts[i][1]
            total += (dx**2 + dy**2) ** 0.5
        self.distance = total
        return total


class GridSettings(models.Model):
    """Stores grid configuration for the admin panel"""
    id = models.AutoField(primary_key=True)
    # Grid display settings
    show_grid = models.BooleanField(default=True, help_text='Show grid overlay')
    grid_size = models.IntegerField(default=40, help_text='Grid cell size in pixels')
    grid_opacity = models.FloatField(default=0.5, help_text='Grid line opacity (0-1)')
    
    # Snap settings
    snap_to_grid = models.BooleanField(default=True, help_text='Snap points to grid')
    
    # Label settings
    show_labels = models.BooleanField(default=True, help_text='Show coordinate labels')
    label_interval = models.IntegerField(default=1000, help_text='Label interval in units')
    
    # Metadata
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'grid_settings'
        verbose_name = 'Grid Settings'
        verbose_name_plural = 'Grid Settings'
    
    def __str__(self):
        return f"Grid Settings ({self.grid_size}px, {'ON' if self.show_grid else 'OFF'})"
    
    @classmethod
    def get_settings(cls):
        """Get or create default grid settings"""
        settings, created = cls.objects.get_or_create(pk=1, defaults={
            'show_grid': True,
            'grid_size': 40,
            'grid_opacity': 0.5,
            'snap_to_grid': True,
            'show_labels': True,
            'label_interval': 1000
        })
        return settings
