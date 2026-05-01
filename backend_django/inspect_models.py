import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'technopath.settings')
django.setup()

from django.apps import apps
from django.db import models

schema = {}
for model in apps.get_models():
    if not model._meta.app_label in ['users', 'core', 'announcements', 'chatbot', 'facilities', 'feedback', 'navigation', 'notifications', 'rooms']:
        continue
    table_name = model._meta.db_table
    schema[table_name] = {'app': model._meta.app_label, 'model_name': model.__name__, 'fields': []}
    for field in model._meta.get_fields():
        if isinstance(field, models.Field):
            fk_model = ""
            if field.is_relation and hasattr(field, 'related_model') and field.related_model:
                fk_model = field.related_model._meta.db_table
            
            verbose_name = str(field.verbose_name) if hasattr(field, 'verbose_name') else str(field.name)
            help_text = str(field.help_text) if hasattr(field, 'help_text') else ''
            
            schema[table_name]['fields'].append({
                'name': field.column,
                'django_name': field.name,
                'type': field.get_internal_type(),
                'null': field.null,
                'pk': field.primary_key,
                'fk': True if field.is_relation else False,
                'fk_table': fk_model,
                'verbose_name': verbose_name,
                'help_text': help_text,
                'max_length': getattr(field, 'max_length', None)
            })

with open('schema_dump.json', 'w') as f:
    json.dump(schema, f, indent=4)
print("Done dumping schema to schema_dump.json")
