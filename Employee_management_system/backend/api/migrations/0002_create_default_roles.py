from django.db import migrations
from django.utils import timezone

def create_roles(apps, schema_editor):
    Role = apps.get_model('api', 'Role')

    default_roles = [
        {'name': 'Admin', 'description': 'System Administrator'},
        {'name': 'Manager', 'description': 'Team or Project Manager'},
        {'name': 'Employee', 'description': 'Standard Employee'},
    ]

    for role_data in default_roles:
        Role.objects.get_or_create(
            name=role_data['name'],
            defaults={
                'description': role_data['description'],
                'created_at': timezone.now(),
                'updated_at': timezone.now(),
            }
        )

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_roles),
    ]
