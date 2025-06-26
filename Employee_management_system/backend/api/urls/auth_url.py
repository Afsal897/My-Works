from django.urls import path
from api.views import auth_view 
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register_admin/', auth_view.register_admin, name='register_admin'),
    path('register_user/', auth_view.register_employee_or_manager, name='register_employee_or_manager'),
    path('login/', auth_view.login_user, name='login_user'),
    path('changepassword/', auth_view.change_password, name='changepassword'),    
    path('change_user_role/', auth_view.change_userrole, name='changerole'),
    path('delete_user/', auth_view.delete_user, name='delete_user'),
    path('list_user/', auth_view.list_users_with_roles, name='list_user'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    ]
