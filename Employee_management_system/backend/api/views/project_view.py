from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from api.serializers import ProjectSerializer, ProjectAssignmentSerializer, ProjectTechnologySerializer
from api.utils import is_admin, is_manager
from api.models import EmployeeProfile, ProjectAssignment, ProjectTechnology

@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_project(request):
    user = request.user

    # Allow only Admins and Managers
    if not (is_admin(user) or is_manager(user)):
        return Response({'error': 'Only Admins and Managers can create projects.'}, status=status.HTTP_403_FORBIDDEN)

    data = request.data.copy()
    # Automatically assign current user as creator
    data['created_by'] = user.id

    #check if that users role is manager
    manager_id = data.get('manager')
    if manager_id:
        try:
            manager_profile = EmployeeProfile.objects.get(pk=manager_id)
        except EmployeeProfile.DoesNotExist:
            return Response({'error': 'Manager profile not found.'}, status=status.HTTP_400_BAD_REQUEST)

        manager_user = manager_profile.user
        if not is_manager(manager_user):
            return Response({'error': 'Selected employee is not a Manager.'}, status=status.HTTP_400_BAD_REQUEST)

    # Validate and save
    serializer = ProjectSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def assign_employee_to_project(request):
    user = request.user

    if not (is_admin(user) or is_manager(user)):
        return Response({'error': 'Only Admins and Managers can assign employees to projects.'},
                        status=status.HTTP_403_FORBIDDEN)

    data = request.data.copy()
    # Auto-assign the assigner
    data['assigned_by'] = user.id  

    # Check for duplicate (project, employee)
    project_id = data.get('project')
    employee_id = data.get('employee')

    if ProjectAssignment.objects.filter(
        project_id=project_id,
        employee_id=employee_id,
        deleted_at__isnull=True
    ).exists():
        return Response({'error': 'This employee is already assigned to this project.'},
                        status=status.HTTP_400_BAD_REQUEST)

    serializer = ProjectAssignmentSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def assign_project_technology(request):
    user = request.user

    #Only Admins and Managers can assign technologies
    if not (is_admin(user) or is_manager(user)):
        return Response(
            {'error': 'Only Admins and Managers can assign technologies to projects.'},
            status=status.HTTP_403_FORBIDDEN
        )

    data = request.data.copy()

    #Uniqueness Check
    project_id = data.get('project')
    skill_id = data.get('skill')

    if ProjectTechnology.objects.filter(
        project_id=project_id,
        skill_id=skill_id,
        deleted_at__isnull=True
    ).exists():
        return Response(
            {'error': 'This technology is already assigned to the project.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = ProjectTechnologySerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)