from django.urls import path
from api.views import leave_view

urlpatterns = [
    path('apply_leave/',leave_view.submit_leave_request, name = "apply leave"),
]
