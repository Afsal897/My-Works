from django.urls import path
from api.views import employee_view

urlpatterns = [
    path('add_profile/',employee_view.create_employee_profile, name = "create_profile"),
    path('add_department/',employee_view.create_department, name="create_department")
]