from django.db import models
from .auth_models import User
from .employee_models import EmployeeProfile
from .project_models import Project

class Timesheet(models.Model):
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()
    work_description = models.TextField(null=True, blank=True)
    hours_worked = models.FloatField()
    submitted_on = models.DateTimeField()
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

class Payroll(models.Model):
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE)
    month = models.CharField(max_length=7)  # Format YYYY-MM
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    allowances = models.DecimalField(max_digits=10, decimal_places=2)
    deductions = models.DecimalField(max_digits=10, decimal_places=2)
    net_pay = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    processed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
