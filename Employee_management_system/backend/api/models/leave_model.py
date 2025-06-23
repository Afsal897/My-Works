from django.db import models
from .auth_models import User
from .employee_models import EmployeeProfile
from django.utils.timezone import now

class Leave(models.Model):
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE)
    
    LEAVE_TYPE_CHOICES = [
        ('sick', 'Sick'),
        ('vacation', 'Vacation'),
        ('personal', 'Personal'),
        ('other', 'Other')
    ]
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(null=True, blank=True)
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    requested_on = models.DateTimeField(default=now)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    approved_on = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

class LeaveBalance(models.Model):
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=20, choices=Leave.LEAVE_TYPE_CHOICES)
    balance = models.FloatField()
    lop_count = models.FloatField(default=0.0)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('employee', 'leave_type')
