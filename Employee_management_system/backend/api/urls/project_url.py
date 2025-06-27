from django.urls import path
from api.views import project_view

urlpatterns = [
    path('add_project/',project_view.create_project, name = "create_project"),
    path('add_employee_to_project/',project_view.assign_employee_to_project, name = "assign_employee_to_project"),
    path('add_project_technologies/',project_view.assign_project_technology, name = "add_project_technologies"),
    path('edit_project/',project_view.edit_project, name = "edit_project"),
    path('delete_project/',project_view.delete_project, name = "delete_project"),
    path('remove_employee_from_project/',project_view.remove_employee_from_project, name = "remove_employee_from_project"),
    path('remove_project_technology/',project_view.remove_project_technology, name = "remove_project_technology"),
    path('list_projects_with_details/',project_view.list_projects_with_details, name = "list_projects_with_details"),
    path('complete_project/',project_view.complete_project, name = "complete_project"),
    ]