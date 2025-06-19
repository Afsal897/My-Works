from django.urls import path
from api.views import auth_view 

urlpatterns = [
    path('register_admin/', auth_view.register_admin, name='register_admin'),
    path('register_user/', auth_view.register_employee_or_manager, name='register_employee_or_manager'),
    path('login/', auth_view.login_user, name='login_user'),
    ]
