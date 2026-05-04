"""
Seed initial training data for the ML intent classifier.
Run this after migrations to populate training examples.

Usage:
    python manage.py seed_training_data
    python manage.py seed_training_data --reset  # Clear existing first
"""

from django.core.management.base import BaseCommand
from apps.chatbot.models import TrainingData


class Command(BaseCommand):
    help = 'Seed initial training data for ML intent classifier'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing training data before seeding',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('Deleting existing training data...')
            TrainingData.objects.filter(source='manual').delete()

        # Initial seed training data - examples for each intent
        training_examples = [
            # Library Hours intent
            {"query_text": "What time does the library open?", "intent_label": "library_hours"},
            {"query_text": "Library hours today", "intent_label": "library_hours"},
            {"query_text": "When does the library close?", "intent_label": "library_hours"},
            {"query_text": "Is the library open on Saturday?", "intent_label": "library_hours"},
            {"query_text": "Library schedule", "intent_label": "library_hours"},
            {"query_text": "What time does LRC open?", "intent_label": "library_hours"},

            # Registrar intent
            {"query_text": "Where is the registrar office?", "intent_label": "registrar"},
            {"query_text": "How to get transcript of records?", "intent_label": "registrar"},
            {"query_text": "Enrollment requirements", "intent_label": "registrar"},
            {"query_text": "How to enroll in classes?", "intent_label": "registrar"},
            {"query_text": "Where can I pay tuition?", "intent_label": "registrar"},
            {"query_text": "Registrar office location", "intent_label": "registrar"},

            # Dean Office intent
            {"query_text": "Where is the dean's office?", "intent_label": "dean_office"},
            {"query_text": "I need to see the dean", "intent_label": "dean_office"},
            {"query_text": "Dean office hours", "intent_label": "dean_office"},
            {"query_text": "Office of the dean location", "intent_label": "dean_office"},

            # Room Location intent
            {"query_text": "Where is CL3?", "intent_label": "room_location"},
            {"query_text": "Computer lab 5 location", "intent_label": "room_location"},
            {"query_text": "Where is the library?", "intent_label": "room_location"},
            {"query_text": "MST building room 301", "intent_label": "room_location"},
            {"query_text": "Where is room 205?", "intent_label": "room_location"},
            {"query_text": "RST building rooms", "intent_label": "room_location"},
            {"query_text": "Where is the cafeteria?", "intent_label": "room_location"},
            {"query_text": "Gymnasium location", "intent_label": "room_location"},

            # Schedule intent
            {"query_text": "Class schedule", "intent_label": "schedule"},
            {"query_text": "What time is lunch break?", "intent_label": "schedule"},
            {"query_text": "School hours", "intent_label": "schedule"},
            {"query_text": "When does the first class start?", "intent_label": "schedule"},
            {"query_text": "Office hours", "intent_label": "schedule"},
            {"query_text": "What time does school end?", "intent_label": "schedule"},

            # Admission intent
            {"query_text": "How to apply for admission?", "intent_label": "admission"},
            {"query_text": "Admission requirements", "intent_label": "admission"},
            {"query_text": "Enrollment process", "intent_label": "admission"},
            {"query_text": "How to become a student here?", "intent_label": "admission"},
            {"query_text": "Transfer student requirements", "intent_label": "admission"},

            # Scholarship intent
            {"query_text": "Available scholarships", "intent_label": "scholarship"},
            {"query_text": "How to apply for scholarship?", "intent_label": "scholarship"},
            {"query_text": "Free tuition", "intent_label": "scholarship"},
            {"query_text": "Financial assistance", "intent_label": "scholarship"},
            {"query_text": "Scholarship requirements", "intent_label": "scholarship"},

            # IT Support intent
            {"query_text": "Wifi password", "intent_label": "it_support"},
            {"query_text": "Internet not working", "intent_label": "it_support"},
            {"query_text": "Computer problem", "intent_label": "it_support"},
            {"query_text": "IT help desk", "intent_label": "it_support"},
            {"query_text": "Reset my password", "intent_label": "it_support"},

            # Safety/Security intent
            {"query_text": "Security office", "intent_label": "safety_security"},
            {"query_text": "Lost and found", "intent_label": "safety_security"},
            {"query_text": "Emergency contact", "intent_label": "safety_security"},
            {"query_text": "Campus safety", "intent_label": "safety_security"},
            {"query_text": "Where is the guard house?", "intent_label": "safety_security"},

            # About SEAIT intent
            {"query_text": "Tell me about SEAIT", "intent_label": "about_seait"},
            {"query_text": "What is SEAIT?", "intent_label": "about_seait"},
            {"query_text": "SEAIT background", "intent_label": "about_seait"},
            {"query_text": "History of SEAIT", "intent_label": "about_seait"},
            {"query_text": "About this school", "intent_label": "about_seait"},
            {"query_text": "What does SEAIT stand for?", "intent_label": "about_seait"},
            {"query_text": "School information", "intent_label": "about_seait"},
            {"query_text": "SEAIT history", "intent_label": "about_seait"},

            # Free Tuition intent
            {"query_text": "Is SEAIT free?", "intent_label": "free_tuition"},
            {"query_text": "Free tuition", "intent_label": "free_tuition"},
            {"query_text": "How much is the tuition?", "intent_label": "free_tuition"},
            {"query_text": "Tuition fee", "intent_label": "free_tuition"},
            {"query_text": "Is college free here?", "intent_label": "free_tuition"},
            {"query_text": "Do I pay tuition?", "intent_label": "free_tuition"},
            {"query_text": "Tuition cost", "intent_label": "free_tuition"},
            {"query_text": "Is education free at SEAIT?", "intent_label": "free_tuition"},

            # Founders intent
            {"query_text": "Who founded SEAIT?", "intent_label": "founders"},
            {"query_text": "Who owns SEAIT?", "intent_label": "founders"},
            {"query_text": "Who started this school?", "intent_label": "founders"},
            {"query_text": "Tell me about the founder", "intent_label": "founders"},
            {"query_text": "Who is the owner?", "intent_label": "founders"},
            {"query_text": "Tamayo family", "intent_label": "founders"},
            {"query_text": "School founder", "intent_label": "founders"},
            {"query_text": "Who established SEAIT?", "intent_label": "founders"},

            # Courses intent
            {"query_text": "What courses do you offer?", "intent_label": "courses"},
            {"query_text": "Available programs", "intent_label": "courses"},
            {"query_text": "Degree programs", "intent_label": "courses"},
            {"query_text": "What can I study here?", "intent_label": "courses"},
            {"query_text": "List of courses", "intent_label": "courses"},
            {"query_text": "How many courses does SEAIT have?", "intent_label": "courses"},
            {"query_text": "How many courses", "intent_label": "courses"},
            {"query_text": "Number of courses", "intent_label": "courses"},
            {"query_text": "What programs are available?", "intent_label": "courses"},
            {"query_text": "Course offerings", "intent_label": "courses"},
            {"query_text": "What degrees do you have?", "intent_label": "courses"},
            {"query_text": "BSIT", "intent_label": "courses"},
            {"query_text": "Computer Science", "intent_label": "courses"},
            {"query_text": "Criminology program", "intent_label": "courses"},
            {"query_text": "Hospitality management", "intent_label": "courses"},
            {"query_text": "Business Administration", "intent_label": "courses"},
            {"query_text": "Electrical Technology", "intent_label": "courses"},
            {"query_text": "Senior high school tracks", "intent_label": "courses"},
            {"query_text": "SHS strands", "intent_label": "courses"},

            # Contact intent
            {"query_text": "How to contact SEAIT?", "intent_label": "contact"},
            {"query_text": "SEAIT contact number", "intent_label": "contact"},
            {"query_text": "Email address", "intent_label": "contact"},
            {"query_text": "Phone number", "intent_label": "contact"},
            {"query_text": "Where is SEAIT located?", "intent_label": "contact"},
            {"query_text": "School address", "intent_label": "contact"},
            {"query_text": "How to reach SEAIT?", "intent_label": "contact"},
            {"query_text": "Contact information", "intent_label": "contact"},

            # General intent (catch-all)
            {"query_text": "Hello", "intent_label": "general"},
            {"query_text": "Hi there", "intent_label": "general"},
            {"query_text": "Good morning", "intent_label": "general"},
            {"query_text": "Thank you", "intent_label": "general"},
            {"query_text": "Goodbye", "intent_label": "general"},
            {"query_text": "Campus map", "intent_label": "general"},
        ]

        created_count = 0
        skipped_count = 0

        for example in training_examples:
            # Check if already exists
            exists = TrainingData.objects.filter(
                query_text__iexact=example['query_text'],
                intent_label=example['intent_label']
            ).exists()

            if not exists:
                TrainingData.objects.create(
                    query_text=example['query_text'],
                    intent_label=example['intent_label'],
                    source='manual',
                    used_for_training=False
                )
                created_count += 1
                self.stdout.write(f"  Created: {example['query_text'][:50]}...")
            else:
                skipped_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'\nSeeding complete! Created {created_count} examples, skipped {skipped_count} duplicates.'
        ))
        self.stdout.write(f'Total training examples: {TrainingData.objects.count()}')
