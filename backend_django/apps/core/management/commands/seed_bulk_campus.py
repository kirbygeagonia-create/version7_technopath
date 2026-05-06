"""
Bulk seed ~1000+ rows (rooms, FAQs, chat logs, map labels/markers) for demos and dashboard stats.

Usage:
  python manage.py seed_bulk_campus
  python manage.py seed_bulk_campus --purge   # remove rows tagged by this command first

Requires core facilities (run seed_default_data once if DB is empty). Safe to re-run: skips
rooms that already match room_number; skips duplicate FAQ/chat batches if already present.
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.facilities.models import Facility
from apps.rooms.models import Room
from apps.chatbot.models import FAQEntry, AIChatLog
from apps.core.models import MapLabel, MapMarker

SEED_TAG = '[bulk_seed_v1]'
BULK_SESSION = 'bulk_seed_v1'


def _get_facility(code):
    return Facility.objects.filter(code__iexact=code).first()


def _upsert_facility(code, name, description, facility_type, total_floors, building_code):
    fac = _get_facility(code)
    defaults = {
        'name': name,
        'description': description,
        'facility_type': facility_type,
        'building_code': building_code,
        'total_floors': total_floors,
        'is_active': True,
        'is_deleted': False,
    }
    if fac:
        for k, v in defaults.items():
            setattr(fac, k, v)
        fac.save(update_fields=list(defaults.keys()))
        return fac
    return Facility.objects.create(code=code.lower(), **defaults)


class Command(BaseCommand):
    help = 'Seed 1000+ campus records for TechnoPath (rooms, FAQs, logs, map data).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--purge',
            action='store_true',
            help='Remove data previously created by this command (tagged).',
        )

    def handle(self, *args, **options):
        if options['purge']:
            self._purge()
            self.stdout.write(self.style.WARNING('Purge complete.'))

        with transaction.atomic():
            fac_n = self._ensure_facilities()
            rooms_new = self._seed_rooms()
            faq_n = self._seed_faqs()
            logs_n = self._seed_chat_logs()
            labels_n = self._seed_map_labels()
            markers_n = self._seed_map_markers()

        self.stdout.write(
            self.style.SUCCESS(
                f'Bulk seed done. Facilities updated/created: {fac_n}, new rooms: {rooms_new}, '
                f'new FAQs: {faq_n}, chat logs: {logs_n}, map labels: {labels_n}, markers: {markers_n}'
            )
        )

    def _purge(self):
        Room.objects.filter(description__startswith=SEED_TAG).delete()
        FAQEntry.objects.filter(keywords__icontains=BULK_SESSION).delete()
        AIChatLog.objects.filter(session_id=BULK_SESSION).delete()
        MapLabel.objects.filter(label_text__startswith=SEED_TAG).delete()
        MapMarker.objects.filter(name__startswith=SEED_TAG).delete()

    def _ensure_facilities(self):
        specs = [
            ('mst', 'MST Building', 'Main Science and Technology Building', 'academic', 4, 'MST'),
            ('jst', 'JST Building', 'Junior Science and Technology Building', 'academic', 4, 'JST'),
            ('rst', 'RST Building', 'Research Science and Technology Building', 'academic', 3, 'RST'),
            (
                'school_canteen',
                'School Canteen',
                'School canteen and dining commons',
                'dining',
                1,
                'SDCANT',
            ),
            (
                'ply',
                'Playground and Recreational Grounds',
                'Outdoor playground and open recreation',
                'sports',
                1,
                'PLY',
            ),
            ('grandstand', 'Grandstand', 'Sports grandstand and viewing area', 'sports', 1, 'GRAND'),
            ('covered_court', 'Covered Court', 'Multi-purpose covered court', 'sports', 1, 'CCOURT'),
            ('guard_house', 'Guard House', 'Main campus security post', 'service', 1, 'GUARD'),
            ('chapel', 'Chapel', 'Campus chapel', 'service', 1, 'CHAPEL'),
            ('clinic', 'School Clinic', 'Health and wellness clinic', 'service', 1, 'CLINIC'),
        ]
        n = 0
        for code, name, desc, ftype, floors, bcode in specs:
            _upsert_facility(code, name, desc, ftype, floors, bcode)
            n += 1
        return n

    def _seed_mst_jst_rooms(self, facility, abbrev):
        existing = set(Room.objects.filter(facility=facility).values_list('room_number', flat=True))
        batch = []
        for floor in range(1, 5):
            base = floor * 100
            for i in range(1, 22):
                num = base + i
                rn = f'{abbrev}-{num}'
                if rn in existing:
                    continue
                is_lab = i % 4 == 0
                batch.append(
                    Room(
                        facility=facility,
                        name=f'{abbrev} {num}',
                        code=f'{abbrev.lower()}_{num}',
                        room_number=rn,
                        description=f'{SEED_TAG} Classroom/lab grid',
                        floor=floor,
                        room_type='lab' if is_lab else 'classroom',
                        capacity=40 if is_lab else 45,
                        is_active=True,
                    )
                )
        if batch:
            Room.objects.bulk_create(batch, batch_size=400)

    def _seed_rst_offices(self):
        rst = _get_facility('rst')
        if not rst:
            return 0
        existing = set(Room.objects.filter(facility=rst).values_list('room_number', flat=True))
        offices = [
            (1, 'RST-101', 'Registrar Office', 15),
            (1, 'RST-102', 'Accounting Office', 12),
            (1, 'RST-103', 'Cashier', 8),
            (1, 'RST-104', 'Admissions Office', 14),
            (1, 'RST-105', 'Human Resources Office', 12),
            (2, 'RST-201', 'Guidance Office', 20),
            (2, 'RST-202', 'Safety and Security Office', 15),
            (2, 'RST-203', 'Student Affairs Office', 18),
            (2, 'RST-204', 'Scholarship Office', 10),
            (2, 'RST-205', 'Alumni Relations Office', 8),
            (2, 'RST-206', 'NSTP Office', 14),
            (3, 'RST-301', 'CICT Office', 16),
            (3, 'RST-302', 'Laboratory Office', 12),
            (3, 'RST-303', 'Office of the Program Head', 10),
            (3, 'RST-304', 'Office of the Dean', 8),
            (3, 'RST-305', 'Research and Development Office', 12),
            (3, 'RST-306', 'Extension Services Office', 10),
            (3, 'RST-307', 'Quality Assurance Office', 10),
            (3, 'RST-308', 'Procurement Office', 8),
        ]
        batch = []
        for floor, rn, name, cap in offices:
            if rn in existing:
                continue
            batch.append(
                Room(
                    facility=rst,
                    name=name,
                    code=rn.lower().replace('-', '_'),
                    room_number=rn,
                    description=f'{SEED_TAG} Administrative office',
                    floor=floor,
                    room_type='office',
                    capacity=cap,
                    is_office=True,
                    is_active=True,
                )
            )
        if batch:
            Room.objects.bulk_create(batch)
        return len(batch)

    def _seed_supporting_rooms(self):
        created = 0
        plans = [
            ('school_canteen', 'STALL', 14, 1),
            ('ply', 'REC', 10, 1),
            ('grandstand', 'GS', 8, 1),
            ('covered_court', 'CC', 6, 1),
            ('guard_house', 'GH', 4, 1),
            ('chapel', 'CH', 3, 1),
            ('clinic', 'CL', 6, 1),
            ('bed', 'BED', 45, 2),
        ]
        for code, prefix, count, floors in plans:
            fac = _get_facility(code)
            if not fac:
                continue
            existing = set(Room.objects.filter(facility=fac).values_list('room_number', flat=True))
            batch = []
            for fl in range(1, floors + 1):
                for i in range(1, count + 1):
                    rn = f'{prefix}-{fl}-{i:02d}'
                    if rn in existing:
                        continue
                    batch.append(
                        Room(
                            facility=fac,
                            name=f'{fac.name} {prefix} {fl}-{i:02d}',
                            code=f'{fac.code}_{prefix}_{fl}_{i}'.lower()[:50],
                            room_number=rn,
                            description=SEED_TAG,
                            floor=fl,
                            room_type='other',
                            capacity=25,
                            is_active=True,
                        )
                    )
            if batch:
                Room.objects.bulk_create(batch, batch_size=300)
                created += len(batch)
        return created

    def _seed_extra_volume_rooms(self):
        created = 0
        pairs = [('lib', 'LIB', 130), ('caf', 'CAF', 90), ('gym', 'GYM', 40)]
        for code, abbrev, n in pairs:
            fac = _get_facility(code)
            if not fac:
                continue
            existing = set(Room.objects.filter(facility=fac).values_list('room_number', flat=True))
            batch = []
            for i in range(1, n + 1):
                rn = f'{abbrev}-{i:03d}'
                if rn in existing:
                    continue
                batch.append(
                    Room(
                        facility=fac,
                        name=f'{abbrev} space {i:03d}',
                        code=f'{abbrev.lower()}_{i}',
                        room_number=rn,
                        description=SEED_TAG,
                        floor=min(3, (i - 1) // 50 + 1),
                        room_type='classroom' if abbrev == 'LIB' else 'facility',
                        capacity=25,
                        is_active=True,
                    )
                )
            if batch:
                Room.objects.bulk_create(batch, batch_size=250)
                created += len(batch)
        return created

    def _seed_rooms(self):
        before = Room.objects.count()
        mst = _get_facility('mst')
        jst = _get_facility('jst')
        if mst:
            self._seed_mst_jst_rooms(mst, 'MST')
        if jst:
            self._seed_mst_jst_rooms(jst, 'JST')
        self._seed_rst_offices()
        self._seed_supporting_rooms()
        self._seed_extra_volume_rooms()
        return Room.objects.count() - before

    def _seed_faqs(self):
        if FAQEntry.objects.filter(keywords__icontains=BULK_SESSION).count() >= 400:
            self.stdout.write('Skipping FAQ bulk (already seeded).')
            return 0
        batch = [
            FAQEntry(
                question=f'Where is seeded campus zone {i}? ({BULK_SESSION})',
                answer=(
                    f'This is auto-generated FAQ #{i} for TechnoPath demo data. '
                    f'Use Navigate or ask staff for the exact location.'
                ),
                category='location',
                keywords=f'campus,navigation,seed,{BULK_SESSION},zone{i}',
                is_deleted=False,
            )
            for i in range(450)
        ]
        FAQEntry.objects.bulk_create(batch, batch_size=200)
        return len(batch)

    def _seed_chat_logs(self):
        if AIChatLog.objects.filter(session_id=BULK_SESSION).count() >= 200:
            self.stdout.write('Skipping chat log bulk (already seeded).')
            return 0
        batch = [
            AIChatLog(
                user_query=f'[bulk_seed] Demo question {i} about the campus?',
                ai_response=f'Demo reply {i}: use Navigate or the FAQ for details.',
                mode='offline',
                response_time_ms=100 + (i % 90),
                is_successful=True,
                session_id=BULK_SESSION,
            )
            for i in range(260)
        ]
        AIChatLog.objects.bulk_create(batch, batch_size=120)
        return len(batch)

    def _seed_map_labels(self):
        if MapLabel.objects.filter(label_text__startswith=SEED_TAG).count() > 80:
            self.stdout.write('Skipping map labels (already seeded).')
            return 0
        titles = [
            'MST Building',
            'JST Building',
            'RST Building',
            'School Canteen',
            'Playground',
            'Library',
            'Gymnasium',
            'Basic Education',
            'Grandstand',
            'Covered Court',
            'Faculty Area',
            'Student Plaza',
            'Parking Area',
            'Motorpool',
            'Campus Garden',
        ]
        batch = []
        for i, text in enumerate(titles):
            batch.append(
                MapLabel(
                    label_text=f'{SEED_TAG} {text}',
                    x_position=0.05 + (i % 5) * 0.18,
                    y_position=0.06 + (i // 5) * 0.11,
                    font_size=12 + (i % 5),
                    is_active=True,
                )
            )
        for j in range(90):
            batch.append(
                MapLabel(
                    label_text=f'{SEED_TAG} Sector {j + 1}',
                    x_position=min(0.92, 0.04 + (j * 0.019) % 0.88),
                    y_position=min(0.92, 0.12 + (j * 0.023) % 0.78),
                    font_size=11,
                    is_active=True,
                )
            )
        MapLabel.objects.bulk_create(batch, batch_size=120)
        return len(batch)

    def _seed_map_markers(self):
        if MapMarker.objects.filter(name__startswith=SEED_TAG).count() > 40:
            self.stdout.write('Skipping map markers (already seeded).')
            return 0
        batch = [
            MapMarker(
                name=f'{SEED_TAG} Waypoint {i + 1}',
                x_position=0.08 + (i * 0.016) % 0.84,
                y_position=0.1 + (i * 0.018) % 0.8,
                marker_type='waypoint',
                is_active=True,
            )
            for i in range(60)
        ]
        MapMarker.objects.bulk_create(batch, batch_size=100)
        return len(batch)
