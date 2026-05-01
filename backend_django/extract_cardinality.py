import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'technopath.settings')
django.setup()

from django.apps import apps
from django.db.models.fields.related import ForeignKey, OneToOneField, ManyToManyField

def extract_relationships():
    models = apps.get_models(include_auto_created=True)
    
    relationships = []
    
    for model in models:
        model_name = model._meta.db_table
        
        for f in model._meta.get_fields():
            if f.is_relation and f.concrete and not f.auto_created:
                related_model = f.related_model
                if not related_model:
                    continue
                related_name = related_model._meta.db_table
                
                cardinality = ""
                comment = ""
                
                null_allowed = getattr(f, 'null', False)
                is_m2m = isinstance(f, ManyToManyField)
                is_fk = isinstance(f, ForeignKey)
                is_o2o = isinstance(f, OneToOneField)
                
                if is_m2m:
                    cardinality = "M:N"
                    comment = f"{model_name} and {related_name} have a many-to-many relationship."
                elif is_o2o:
                    src_side = "0:1" if null_allowed else "1:1"
                    cardinality = f"{src_side} <-> 1:1"
                    comment = f"A {model_name} is exclusively linked to one {related_name}."
                elif is_fk:
                    src_side = "0..*" if null_allowed else "1..*"
                    dst_side = "0:1" if null_allowed else "1:1"
                    cardinality = f"{src_side} <-> {dst_side}"
                    comment = f"Multiple {model_name} can belong to one {related_name}. A {related_name} contains zero or more {model_name}."
                
                relationships.append({
                    "src": model_name,
                    "dst": related_name,
                    "card": cardinality,
                    "desc": getattr(f, 'help_text', '') or getattr(f, 'verbose_name', f.name).capitalize(),
                    "comment": comment
                })
                
    with open('Database_Cardinality_Dictionary.md', 'w') as f:
        f.write("# Technopath Database Relationship Cardinality and Comments\n\n")
        
        # Group by source table
        schema = {}
        for r in relationships:
            if r['src'] not in schema:
                schema[r['src']] = []
            schema[r['src']].append(r)
            
        for table, rels in schema.items():
            f.write(f"## Table: `{table}`\n\n")
            for r in rels:
                f.write(f"**{r['src']}** -> **{r['dst']}**\n")
                f.write(f"- **Cardinality**: `{r['card']}`\n")
                f.write(f"- **Field**: {r['desc']}\n")
                f.write(f"- **Comment**: {r['comment']}\n\n")

if __name__ == '__main__':
    extract_relationships()
