from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='course_code',
            field=models.CharField(
                blank=True, null=True, max_length=20,
                help_text='Academic program that primarily uses this room (e.g. BSIT, BSCS)'
            ),
        ),
        migrations.AddField(
            model_name='room',
            name='course_color',
            field=models.CharField(
                blank=True, null=True, max_length=7,
                help_text='Hex highlight color for map (e.g. #FF5722). Auto-assigned if blank.'
            ),
        ),
    ]
