from django.urls import path
from backend.api.views import time_view

urlpatterns=[
    path('submit_timesheet/', time_view.submit_timesheet, name="submit_timesheet"),
    path('payroll/',time_view.add_payroll, name='add payroll')
]