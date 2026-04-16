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
        # ONLY include concrete fields (actual database columns)
        if not hasattr(field, 'concrete') or not field.concrete:
            continue
            
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
            'max_length': getattr(field, 'max_length', None),
            'default': field.default if field.has_default() and field.default is not django.db.models.fields.NOT_PROVIDED else None
        })

with open('schema_dump_fixed.json', 'w') as f:
    # Need to convert un-serializable defaults to string
    def default_serializer(o):
        return str(o)
    json.dump(schema, f, indent=4, default=default_serializer)
print("Done dumping accurate schema.")
