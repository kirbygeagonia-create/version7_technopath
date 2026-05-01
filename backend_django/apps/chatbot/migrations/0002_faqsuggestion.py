# Generated migration for FAQSuggestion model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FAQSuggestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('suggested_question', models.TextField()),
                ('suggested_answer', models.TextField()),
                ('category', models.CharField(choices=[('location', 'Location'), ('schedule', 'Schedule'), ('academic', 'Academic'), ('services', 'Services'), ('general', 'General')], default='general', max_length=50)),
                ('keywords', models.TextField(blank=True, default='')),
                ('source_queries', models.JSONField(default=list, help_text='Original queries that triggered this suggestion')),
                ('query_count', models.IntegerField(default=1, help_text='Number of times similar queries were asked')),
                ('confidence_score', models.FloatField(default=0.0, help_text='AI confidence score (0-1)')),
                ('status', models.CharField(choices=[('pending', 'Pending Review'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('review_note', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('faq_entry', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='chatbot.faqentry')),
                ('reviewed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.adminuser')),
            ],
            options={
                'db_table': 'faq_suggestions',
                'ordering': ['-query_count', '-created_at'],
            },
        ),
    ]
