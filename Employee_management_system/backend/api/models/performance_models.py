from django.db import models
from .auth_models import User
from .employee_models import EmployeeProfile
from .project_models import Project


class PerformanceRating(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE, related_name='ratings')
    rated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.FloatField()
    review_comment = models.TextField(null=True, blank=True)
    review_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)


class TeammateFeedback(models.Model):
    from_employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE, related_name='feedback_given')
    to_employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE, related_name='feedback_received')
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    feedback_text = models.TextField(null=True, blank=True)
    rating = models.FloatField()
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('reviewed', 'Reviewed')
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    submitted_on = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
