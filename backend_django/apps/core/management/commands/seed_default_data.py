"""
Management command to seed default data from Flutter app.
Run: python manage.py seed_default_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from apps.core.models import (
    Department, AppConfig, NotificationType, MapMarker, 
    MapLabel, Rating
)
from apps.facilities.models import Facility
from apps.rooms.models import Room
from apps.navigation.models import NavigationNode, NavigationEdge
from apps.chatbot.models import FAQEntry


class Command(BaseCommand):
    help = 'Seeds default data from Flutter app migration'

    def handle(self, *args, **options):
        self.stdout.write('Seeding default data...')
        
        # Create Departments
        departments_data = [
            {'name': 'Computer Science', 'code': 'CS', 'description': 'Computer Science Department'},
            {'name': 'Information Technology', 'code': 'IT', 'description': 'Information Technology Department'},
            {'name': 'Engineering', 'code': 'ENG', 'description': 'Engineering Department'},
            {'name': 'Safety and Security', 'code': 'SAS', 'description': 'Campus Safety and Security Office'},
            {'name': 'Administration', 'code': 'ADMIN', 'description': 'School Administration'},
        ]
        
        for dept_data in departments_data:
            Department.objects.get_or_create(code=dept_data['code'], defaults=dept_data)
        self.stdout.write(self.style.SUCCESS(f'Created {len(departments_data)} departments'))
        
        # Create Facilities
        facilities_data = [
            {'name': 'RST Building', 'description': 'Research Science and Technology Building', 'building_code': 'RST', 'latitude': 14.1001, 'longitude': 121.0801, 'total_floors': 3},
            {'name': 'JST Building', 'description': 'Junior Science and Technology Building', 'building_code': 'JST', 'latitude': 14.1002, 'longitude': 121.0802, 'total_floors': 4},
            {'name': 'MST Building', 'description': 'Main Science and Technology Building', 'building_code': 'MST', 'latitude': 14.1003, 'longitude': 121.0803, 'total_floors': 4},
            {'name': 'Basic Education Building', 'description': 'Basic Education Department', 'building_code': 'BED', 'latitude': 14.1004, 'longitude': 121.0804, 'total_floors': 2},
            {'name': 'Gymnasium', 'description': 'Sports and Activities Center', 'building_code': 'GYM', 'latitude': 14.1005, 'longitude': 121.0805, 'total_floors': 1},
            {'name': 'Library', 'description': 'School Library and Resource Center', 'building_code': 'LIB', 'latitude': 14.1006, 'longitude': 121.0806, 'total_floors': 2},
            {'name': 'Registrar Office', 'description': 'Student Records and Enrollment', 'building_code': 'REG', 'latitude': 14.1007, 'longitude': 121.0807, 'total_floors': 1},
            {'name': 'Cafeteria', 'description': 'Main Cafeteria and Dining Area', 'building_code': 'CAF', 'latitude': 14.1008, 'longitude': 121.0808, 'total_floors': 1},
            {'name': 'Playground', 'description': 'Student Recreation Area', 'building_code': 'PLY', 'latitude': 14.1009, 'longitude': 121.0809, 'total_floors': 1},
        ]
        
        facilities = []
        for fac_data in facilities_data:
            fac, _ = Facility.objects.get_or_create(
                code=fac_data['building_code'],
                defaults={**fac_data, 'is_active': True}
            )
            facilities.append(fac)
        self.stdout.write(self.style.SUCCESS(f'Created {len(facilities_data)} facilities'))
        
        # Create Rooms
        rooms_data = [
            # RST Building - Ground Floor
            {'facility_code': 'RST', 'name': 'CL1', 'description': 'Computer Lab 1', 'room_number': 'RST-GF-CL1', 'floor': 1, 'room_type': 'lab', 'capacity': 40},
            {'facility_code': 'RST', 'name': 'CL2', 'description': 'Computer Lab 2', 'room_number': 'RST-GF-CL2', 'floor': 1, 'room_type': 'lab', 'capacity': 40},
            {'facility_code': 'RST', 'name': 'CR1', 'description': 'Classroom 1', 'room_number': 'RST-GF-CR1', 'floor': 1, 'room_type': 'classroom', 'capacity': 50},
            {'facility_code': 'RST', 'name': 'CR2', 'description': 'Classroom 2', 'room_number': 'RST-GF-CR2', 'floor': 1, 'room_type': 'classroom', 'capacity': 50},
            # RST Building - 2nd Floor
            {'facility_code': 'RST', 'name': 'CL3', 'description': 'Computer Lab 3', 'room_number': 'RST-2F-CL3', 'floor': 2, 'room_type': 'lab', 'capacity': 40},
            {'facility_code': 'RST', 'name': 'CR3', 'description': 'Classroom 3', 'room_number': 'RST-2F-CR3', 'floor': 2, 'room_type': 'classroom', 'capacity': 50},
            {'facility_code': 'RST', 'name': 'Faculty Office', 'description': 'RST Faculty Office', 'room_number': 'RST-2F-FO', 'floor': 2, 'room_type': 'office', 'capacity': 10, 'is_office': True},
            # JST Building - Ground Floor
            {'facility_code': 'JST', 'name': 'CL4', 'description': 'Computer Lab 4', 'room_number': 'JST-GF-CL4', 'floor': 1, 'room_type': 'lab', 'capacity': 35},
            {'facility_code': 'JST', 'name': 'CR4', 'description': 'Classroom 4', 'room_number': 'JST-GF-CR4', 'floor': 1, 'room_type': 'classroom', 'capacity': 45},
            # JST Building - 2nd Floor
            {'facility_code': 'JST', 'name': 'CL5', 'description': 'Computer Lab 5', 'room_number': 'JST-2F-CL5', 'floor': 2, 'room_type': 'lab', 'capacity': 35},
            {'facility_code': 'JST', 'name': 'CR5', 'description': 'Classroom 5', 'room_number': 'JST-2F-CR5', 'floor': 2, 'room_type': 'classroom', 'capacity': 45},
            # MST Building - Multiple Floors
            {'facility_code': 'MST', 'name': 'CL6', 'description': 'Computer Lab 6', 'room_number': 'MST-GF-CL6', 'floor': 1, 'room_type': 'lab', 'capacity': 50},
            {'facility_code': 'MST', 'name': 'CL7', 'description': 'Computer Lab 7', 'room_number': 'MST-2F-CL7', 'floor': 2, 'room_type': 'lab', 'capacity': 50},
            {'facility_code': 'MST', 'name': 'CICT Office', 'description': 'CICT Department Office', 'room_number': 'MST-2F-CICT', 'floor': 2, 'room_type': 'office', 'capacity': 15, 'is_office': True},
            {'facility_code': 'MST', 'name': 'Dean Office', 'description': 'College Dean Office', 'room_number': 'MST-3F-DEAN', 'floor': 3, 'room_type': 'office', 'capacity': 8, 'is_office': True},
            # BED Building
            {'facility_code': 'BED', 'name': 'BED Classroom 1', 'description': 'Basic Ed Classroom', 'room_number': 'BED-GF-C1', 'floor': 1, 'room_type': 'classroom', 'capacity': 30},
            {'facility_code': 'BED', 'name': 'BED Classroom 2', 'description': 'Basic Ed Classroom', 'room_number': 'BED-2F-C2', 'floor': 2, 'room_type': 'classroom', 'capacity': 30},
        ]
        
        for room_data in rooms_data:
            fac = Facility.objects.filter(code=room_data['facility_code']).first()
            if fac:
                code = room_data.pop('facility_code')
                Room.objects.get_or_create(
                    facility=fac,
                    room_number=room_data['room_number'],
                    defaults={**room_data, 'is_active': True}
                )
        self.stdout.write(self.style.SUCCESS(f'Created {len(rooms_data)} rooms'))
        
        # Create Navigation Nodes
        nodes_data = [
            {'name': 'Main Gate', 'node_type': 'entrance', 'x': 0.5, 'y': 0.9, 'floor': 0},
            {'name': 'RST Node', 'node_type': 'facility', 'facility_code': 'RST', 'x': 0.3, 'y': 0.5, 'floor': 1},
            {'name': 'JST Node', 'node_type': 'facility', 'facility_code': 'JST', 'x': 0.5, 'y': 0.5, 'floor': 1},
            {'name': 'MST Node', 'node_type': 'facility', 'facility_code': 'MST', 'x': 0.7, 'y': 0.5, 'floor': 1},
            {'name': 'BED Node', 'node_type': 'facility', 'facility_code': 'BED', 'x': 0.2, 'y': 0.3, 'floor': 1},
            {'name': 'Gym Node', 'node_type': 'facility', 'facility_code': 'GYM', 'x': 0.8, 'y': 0.3, 'floor': 1},
            {'name': 'Library Node', 'node_type': 'facility', 'facility_code': 'LIB', 'x': 0.4, 'y': 0.2, 'floor': 1},
            {'name': 'Registrar Node', 'node_type': 'facility', 'facility_code': 'REG', 'x': 0.6, 'y': 0.2, 'floor': 1},
            {'name': 'Cafeteria Node', 'node_type': 'facility', 'facility_code': 'CAF', 'x': 0.5, 'y': 0.7, 'floor': 1},
            {'name': 'Playground Node', 'node_type': 'facility', 'facility_code': 'PLY', 'x': 0.9, 'y': 0.7, 'floor': 1},
        ]
        
        nodes = []
        for node_data in nodes_data:
            fac_code = node_data.pop('facility_code', None)
            fac = Facility.objects.filter(code=fac_code).first() if fac_code else None
            node, _ = NavigationNode.objects.get_or_create(
                name=node_data['name'],
                defaults={
                    **node_data,
                    'facility': fac,
                    'x': node_data['x'],
                    'y': node_data['y'],
                }
            )
            nodes.append(node)
        self.stdout.write(self.style.SUCCESS(f'Created {len(nodes_data)} navigation nodes'))
        
        # Create Navigation Edges (pathways)
        edges_data = [
            (0, 8, 2.0, 'walkway'),  # Gate to Cafeteria
            (8, 1, 3.0, 'walkway'),  # Cafeteria to RST
            (8, 2, 2.0, 'walkway'),  # Cafeteria to JST
            (8, 3, 3.0, 'walkway'),  # Cafeteria to MST
            (1, 4, 4.0, 'walkway'),  # RST to BED
            (3, 5, 3.0, 'walkway'),  # MST to Gym
            (1, 6, 2.5, 'walkway'),  # RST to Library
            (2, 6, 1.5, 'walkway'),  # JST to Library
            (2, 7, 1.5, 'walkway'),  # JST to Registrar
            (3, 7, 2.0, 'walkway'),  # MST to Registrar
            (3, 9, 3.0, 'walkway'),  # MST to Playground
        ]
        
        for from_idx, to_idx, distance, edge_type in edges_data:
            if from_idx < len(nodes) and to_idx < len(nodes):
                NavigationEdge.objects.get_or_create(
                    from_node=nodes[from_idx],
                    to_node=nodes[to_idx],
                    defaults={'distance': int(distance * 10), 'is_bidirectional': True}
                )
        self.stdout.write(self.style.SUCCESS(f'Created {len(edges_data)} navigation edges'))
        
        # Create FAQ entries
        faqs_data = [
            {'question': 'Where is the MST Building?', 'answer': 'The MST (Main Science and Technology) Building is located at the center-right of the campus. From the main gate, walk straight past the cafeteria and turn right.', 'keywords': 'mst,main,building,location', 'category': 'navigation'},
            {'question': 'Where is the JST Building?', 'answer': 'The JST (Junior Science and Technology) Building is in the center of the campus, between the Library and the Cafeteria.', 'keywords': 'jst,junior,building,location', 'category': 'navigation'},
            {'question': 'Where is the RST Building?', 'answer': 'The RST (Research Science and Technology) Building is on the left side of the campus, near the Basic Education Building.', 'keywords': 'rst,research,building,location', 'category': 'navigation'},
            {'question': 'Where is the comfort room?', 'answer': 'Comfort rooms are available on each floor of all buildings. The nearest one to the main gate is in the Cafeteria building.', 'keywords': 'comfort room,cr,restroom,toilet,bathroom', 'category': 'facilities'},
            {'question': 'Where is the library?', 'answer': 'The Library is located behind the JST Building, near the Registrar Office.', 'keywords': 'library,books,study', 'category': 'facilities'},
            {'question': 'How do I navigate to a room?', 'answer': 'Use the Navigate tab at the bottom of the screen. Select your destination building and room, and the app will show you the shortest path from the main gate or your current location.', 'keywords': 'navigate,find,go to,how to', 'category': 'help'},
            {'question': 'Where is the CICT office?', 'answer': 'The CICT office is located on the 2nd floor of the MST Building, room MST-2F-CICT.', 'keywords': 'cict,office,department,location', 'category': 'navigation'},
            {'question': 'What are the library hours?', 'answer': 'The Library is open Monday to Friday, 8:00 AM to 6:00 PM, and Saturday, 8:00 AM to 12:00 PM.', 'keywords': 'library,hours,open,time', 'category': 'facilities'},
            {'question': 'Where is the cafeteria?', 'answer': 'The Cafeteria is located straight ahead from the main gate, between the JST and MST buildings.', 'keywords': 'cafeteria,canteen,food,eat', 'category': 'facilities'},
            {'question': 'Where is the Registrar Office?', 'answer': 'The Registrar Office is located behind the JST Building, next to the Library.', 'keywords': 'registrar,office,enrollment,records', 'category': 'facilities'},
        ]
        
        for faq_data in faqs_data:
            FAQEntry.objects.get_or_create(
                question=faq_data['question'],
                defaults={**faq_data, 'is_deleted': False}
            )
        self.stdout.write(self.style.SUCCESS(f'Created {len(faqs_data)} FAQ entries'))
        
        # Create Notification Types
        notif_types_data = [
            {'name': 'general', 'description': 'General announcements', 'icon_name': 'notifications', 'color_hex': '#FF9800'},
            {'name': 'navigation', 'description': 'Navigation updates', 'icon_name': 'navigation', 'color_hex': '#2196F3'},
            {'name': 'emergency', 'description': 'Emergency alerts', 'icon_name': 'warning', 'color_hex': '#F44336'},
            {'name': 'facility', 'description': 'Facility updates', 'icon_name': 'business', 'color_hex': '#4CAF50'},
            {'name': 'system', 'description': 'System notifications', 'icon_name': 'settings', 'color_hex': '#9C27B0'},
        ]
        
        for nt_data in notif_types_data:
            NotificationType.objects.get_or_create(
                name=nt_data['name'],
                defaults={**nt_data, 'is_active': True}
            )
        self.stdout.write(self.style.SUCCESS(f'Created {len(notif_types_data)} notification types'))
        
        # Create App Config
        configs_data = [
            {'config_key': 'app_version', 'config_value': '1.0.0', 'description': 'Current app version'},
            {'config_key': 'offline_mode_enabled', 'config_value': 'true', 'description': 'Allow offline operation'},
            {'config_key': 'qr_code_enabled', 'config_value': 'true', 'description': 'Enable QR code scanning'},
            {'config_key': 'navigation_enabled', 'config_value': 'true', 'description': 'Enable navigation features'},
            {'config_key': 'maintenance_mode', 'config_value': 'false', 'description': 'App maintenance status'},
        ]
        
        for config_data in configs_data:
            AppConfig.objects.get_or_create(
                config_key=config_data['config_key'],
                defaults=config_data
            )
        self.stdout.write(self.style.SUCCESS(f'Created {len(configs_data)} app config entries'))
        
        # Create Map Markers
        markers_data = [
            {'name': 'Building', 'x': 0.3, 'y': 0.4, 'type': 'facility'},
            {'name': 'RST Building', 'x': 0.6, 'y': 0.3, 'type': 'facility'},
            {'name': 'JST Building', 'x': 0.4, 'y': 0.6, 'type': 'facility'},
            {'name': 'MST Building', 'x': 0.7, 'y': 0.5, 'type': 'facility'},
            {'name': 'CL1', 'x': 0.25, 'y': 0.35, 'type': 'room'},
            {'name': 'CL2', 'x': 0.35, 'y': 0.35, 'type': 'room'},
            {'name': 'CL3', 'x': 0.25, 'y': 0.45, 'type': 'room'},
            {'name': 'CL4', 'x': 0.35, 'y': 0.45, 'type': 'room'},
        ]
        
        for marker_data in markers_data:
            MapMarker.objects.get_or_create(
                name=marker_data['name'],
                defaults={
                    'x_position': marker_data['x'],
                    'y_position': marker_data['y'],
                    'marker_type': marker_data['type'],
                    'is_active': True
                }
            )
        self.stdout.write(self.style.SUCCESS(f'Created {len(markers_data)} map markers'))
        
        self.stdout.write(self.style.SUCCESS('Default data seeding completed!'))
