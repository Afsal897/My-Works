# Generated by Django 5.2.3 on 2025-06-20 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_delete_supportrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
