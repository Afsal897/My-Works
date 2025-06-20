from django.urls import path
from api.views import support_view

urlpatterns=[
    path('submit_resignation/', support_view.submit_resignation, name="submit_resignation"),
    # path('payroll/',support_view.add_payroll, name='add payroll')
]