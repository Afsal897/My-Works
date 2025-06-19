from django.urls import path
from api.views import project_view

urlpatterns = [
    path('add_project/',project_view.create_project, name = "create_project"),
    path('add_employee_to_project/',project_view.assign_employee_to_project, name = "assign_employee_to_project"),
    path('add_project_technologies/',project_view.assign_project_technology, name = "add_project_technologies")
]