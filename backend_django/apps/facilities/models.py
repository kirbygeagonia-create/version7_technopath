from django.db import models

class Facility(models.Model):
    FACILITY_TYPES = [
        ('academic', 'Academic Building'),
        ('administrative', 'Administrative'),
        ('library', 'Library'),
        ('sports', 'Sports & Recreation'),
        ('dining', 'Dining'),
        ('service', 'Service Facility'),
    ]

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    facility_type = models.CharField(max_length=20, choices=FACILITY_TYPES, default='academic')
    building_code = models.CharField(max_length=20, blank=True, null=True)
    department = models.ForeignKey('core.Department', on_delete=models.SET_NULL, null=True, blank=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    x_position = models.FloatField(blank=True, null=True, help_text='SVG-relative X position (0.0–1.0)')
    y_position = models.FloatField(blank=True, null=True, help_text='SVG-relative Y position (0.0–1.0)')
    image_path = models.CharField(max_length=500, blank=True, null=True)
    map_svg_id = models.CharField(max_length=100, blank=True, null=True, help_text='SVG element ID e.g. building-RST')
    total_floors = models.IntegerField(default=1)
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'facilities'

    def __str__(self):
        return self.name

