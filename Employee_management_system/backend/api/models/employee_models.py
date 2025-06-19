from django.db import models
from .auth_models import User

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    head = models.ForeignKey(
        'EmployeeProfile',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='headed_departments'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

class EmployeeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey('Department', on_delete=models.CASCADE, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    designation = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    join_date = models.DateField()
    profile_picture = models.CharField(max_length=255, null=True, blank=True)
    supervisor = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
