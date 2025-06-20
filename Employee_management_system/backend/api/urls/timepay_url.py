from django.urls import path
from api.views import timepay_view

urlpatterns=[
    path('submit_timesheet/', timepay_view.submit_timesheet, name="submit_timesheet"),
    path('payroll/',timepay_view.add_payroll, name='add payroll')
]