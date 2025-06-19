from django.urls import path
from api.views import skill_view

urlpatterns = [
    path('add_skill/',skill_view.create_skill, name = "create_skill"),
    path('employee_skill/',skill_view.add_employee_skill, name = "employee_skill")
]