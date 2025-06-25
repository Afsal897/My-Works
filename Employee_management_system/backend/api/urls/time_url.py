from django.urls import path
from api.views import time_view

urlpatterns=[
    path('submit_timesheet/', time_view.submit_timesheet, name="submit_timesheet")
]