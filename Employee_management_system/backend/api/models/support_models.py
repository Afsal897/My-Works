from django.db import models
from .auth_models import User
from .employee_models import EmployeeProfile

class Resignation(models.Model):
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

class SupportRequest(models.Model):
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    message = models.TextField()
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed')
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    submitted_on = models.DateTimeField()
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    resolved_on = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
