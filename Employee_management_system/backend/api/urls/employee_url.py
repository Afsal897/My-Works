from django.urls import path
from api.views import employee_view

urlpatterns = [
    path('add_profile/',employee_view.create_employee_profile, name = "create_profile"),
    path('add_department/',employee_view.create_department, name="create_department"),
    path('create_designation/',employee_view.create_designation, name="create_designation"),
    path('edit_department/',employee_view.edit_department, name = "edit_department"),
    path('delete_department/',employee_view.delete_department, name = "delete_department"),
    path('edit_employee_profile/',employee_view.edit_employee_profile, name = "edit_employee_profile"),
    path('list_departments/',employee_view.list_departments, name = "list_departments"),
    path('list_designations/',employee_view.list_designations, name = "list_designations"),
    path('list_employees/',employee_view.list_employees, name = "list_employees")
]