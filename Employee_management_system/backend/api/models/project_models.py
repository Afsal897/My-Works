from django.db import models
from datetime import datetime
from .auth_models import User
from .employee_models import EmployeeProfile
from .skill_models import Skill


class Project(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_projects')
    manager = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE, related_name='managed_projects')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)


class ProjectAssignment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE)
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE)
    assigned_on = models.DateTimeField(default=datetime.now)
    
    ASSIGNMENT_STATUS = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('removed', 'Removed')
    ]
    assignment_status = models.CharField(max_length=20, choices=ASSIGNMENT_STATUS, default='active')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('project', 'employee')


class ProjectTechnology(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('project', 'skill')
        verbose_name_plural = 'Project Technologies'

    def __str__(self):
        return f"{self.project.name} - {self.skill.name}"