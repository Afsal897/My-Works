from django.urls import path
from api.views import skill_view

urlpatterns = [
    path('add_skill/',skill_view.create_skill, name = "create_skill"),
    path('employee_skill/',skill_view.add_employee_skill, name = "employee_skill"),
    path('edit_skill/',skill_view.edit_skill, name = "edit_skill"),
    path('delete_skill/',skill_view.delete_skill, name = "delete_skill"),
    path('remove_employee_skill/',skill_view.remove_employee_skill, name = "remove_employee_skill"),
    path('list_all_skills/',skill_view.list_all_skills, name = "list_all_skills"),
    path('list_employee_skills/',skill_view.list_employee_skills, name = "list_employee_skills")
]