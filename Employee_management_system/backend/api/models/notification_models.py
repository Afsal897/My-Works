from django.db import models
from .auth_models import User

class Notification(models.Model):
    title = models.CharField(max_length=100)
    message = models.TextField()
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    
    EVENT_CHOICES = [
        ('rating', 'Rating'),
        ('assignment', 'Assignment'),
        ('leave', 'Leave'),
        ('support', 'Support'),
        ('other', 'Other')
    ]
    event_type = models.CharField(max_length=20, choices=EVENT_CHOICES)
    related_entity_id = models.IntegerField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
