from django.urls import path
from api.views import project_view

urlpatterns = [
    path('add_project/',project_view.create_project, name = "create_project")
]