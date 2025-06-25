from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime


class User(AbstractUser):
    email = models.EmailField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']  # Required when creating superusers

    def __str__(self):
        return self.username


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)


class UserRole(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE)#user only appear once
    role = models.ForeignKey('Role', on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(default=datetime.now)

    class Meta:
        unique_together = ('user', 'role')
