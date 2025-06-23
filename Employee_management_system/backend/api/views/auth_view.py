from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from api.serializers import UserSerializer, LoginSerializer, ChangePasswordSerializer, ChangeUserRoleSerializer, DeleteUserSerializer
from api.models import Role, UserRole
from api.utils import is_admin

User = get_user_model()

@api_view(['POST'])
def register_admin(request):
    # Check if an admin already exists
    try:
        admin_role = Role.objects.get(name='Admin')
        admin_exists = UserRole.objects.filter(role=admin_role).exists()
    except Role.DoesNotExist:
        admin_role = Role.objects.create(name='Admin')
        admin_role = Role.objects.create(name='Manager')
        admin_role = Role.objects.create(name='Employee')
        admin_exists = False

    if admin_exists:
        return Response({'error': 'Admin user already exists.'}, status=status.HTTP_403_FORBIDDEN)

    # Proceed to register the user
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()

        # Assign 'Admin' role to the newly registered user
        UserRole.objects.create(user=user, role=admin_role)

        return Response({'message': 'Admin user registered successfully.'}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@transaction.atomic
def register_employee_or_manager(request):
    #Check if logged-in user is Admin
    user = request.user
    if not is_admin(user):
        return Response({'error': 'Only Admins are allowed to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
    
    #Extract and validate role
    role_name = request.data.get("role", "Employee").capitalize()
    if role_name not in ["Employee", "Manager"]:
        return Response({"error": "Role must be either 'Employee' or 'Manager'."}, status=status.HTTP_400_BAD_REQUEST)

    #Ensure role exists
    role, _ = Role.objects.get_or_create(name=role_name)

    #Validate user data
    user_data = {
        "username": request.data.get("username"),
        "email": request.data.get("email"),
        "password": request.data.get("password"),
        "confirm_password": request.data.get("confirm_password")
    }

    user_serializer = UserSerializer(data=user_data)
    if not user_serializer.is_valid():
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    #Save user
    user = user_serializer.save()

    #Assign role
    UserRole.objects.create(user=user, role=role)

    return Response({'message': f'{role_name} user registered successfully.'}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def login_user(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']

        # Get user's role
        user_role = UserRole.objects.filter(user=user).first()
        role_name = user_role.role.name if user_role else None

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return Response({
            'message': 'Login successful',
            'access': access_token,
            'refresh': str(refresh),
            'user_id': user.id,
            'username': user.username,
            'role': role_name
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    serializer = ChangePasswordSerializer(data=request.data)

    if serializer.is_valid():
        old_password = serializer.validated_data["old_password"]
        new_password = serializer.validated_data["new_password"]

        if not user.check_password(old_password):
            return Response({"old_password": "Incorrect old password."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def change_userrole(request):
    user = request.user
    if not is_admin(user):
        return Response({'error': 'Only Admins are allowed to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = ChangeUserRoleSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Role changed successfully"}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_user(request):
    if not is_admin(request.user):
        return Response({"error":"only admins can delete accounts"}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = DeleteUserSerializer(data = request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User deleted (soft delete)."}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

