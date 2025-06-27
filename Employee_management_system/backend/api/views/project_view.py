from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from api.serializers import (
    ProjectSerializer, 
    EditProjectSerializer,
    DeleteProjectSerializer,
    ProjectAssignmentSerializer,
    RemoveProjectAssignmentSerializer,
    ProjectTechnologySerializer,
    RemoveProjectTechnologySerializer,
    ProjectDetailedSerializer,
    CompleteProjectSerializer
    )
from api.utils import is_admin, is_manager
from api.models import EmployeeProfile, ProjectAssignment, ProjectTechnology, Project, Skill


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


@api_view(["PUT"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def edit_project(request):
    user = request.user
    serializer = EditProjectSerializer(data=request.data, context={'user': user})
    if serializer.is_valid():
        updated_project = serializer.save()
        return Response(EditProjectSerializer(updated_project).data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_project(request):
    user = request.user
    serializer = DeleteProjectSerializer(data=request.data, context={'user': user})
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Project deleted successfully."}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@transaction.atomic
def complete_project(request):
    user = request.user

    if not (is_admin(user) or is_manager(user)):
        return Response({'error': 'Only Admins and Managers can complete projects.'}, status=status.HTTP_403_FORBIDDEN)

    serializer = CompleteProjectSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Project marked as completed and all assignments closed."}, status=status.HTTP_200_OK)

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
    data['assigned_by'] = user.id

    project_id = data.get('project')
    employee_id = data.get('employee')

    # Check if this employee is already assigned to this project
    if ProjectAssignment.objects.filter(
        project_id=project_id,
        employee_id=employee_id,
        deleted_at__isnull=True
    ).exists():
        return Response({'error': 'This employee is already assigned to this project.'},
                        status=status.HTTP_409_CONFLICT)

    # Get the employee's user type
    try:
        employee_profile = EmployeeProfile.objects.get(id=employee_id)
    except EmployeeProfile.DoesNotExist:
        return Response({'error': 'Employee not found.'}, status=status.HTTP_400_BAD_REQUEST)

    employee_user = employee_profile.user

    # Only restrict multiple active project assignments for non-managers
    if not is_manager(employee_user):
        if ProjectAssignment.objects.filter(
            employee_id=employee_id,
            assignment_status='active',
            deleted_at__isnull=True
        ).exists():
            return Response({'error': 'Employee is already actively assigned to another project.'},
                            status=status.HTTP_400_BAD_REQUEST)

    serializer = ProjectAssignmentSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def remove_employee_from_project(request):
    user = request.user
    serializer = RemoveProjectAssignmentSerializer(data=request.data, context={'user': user})
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Employee removed from project."}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def assign_project_technology(request):
    user = request.user

    if not (is_admin(user) or is_manager(user)):
        return Response(
            {'error': 'Only Admins and Managers can assign technologies to projects.'},
            status=status.HTTP_403_FORBIDDEN
        )

    data = request.data.copy()
    project_id = data.get('project')
    skill_id = data.get('skill')

    # Check if the skill itself is soft-deleted
    try:
        skill = Skill.objects.get(id=skill_id)
        if skill.deleted_at is not None:
            return Response(
                {'error': 'Cannot assign a deleted (inactive) skill to a project.'},
                status=status.HTTP_400_BAD_REQUEST
            )
    except Skill.DoesNotExist:
        return Response(
            {'error': 'Skill does not exist.'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Prevent duplicate active assignment
    if ProjectTechnology.objects.filter(
        project_id=project_id,
        skill_id=skill_id,
        deleted_at__isnull=True
    ).exists():
        return Response(
            {'error': 'This technology is already assigned to the project.'},
            status=status.HTTP_409_CONFLICT
        )  

    serializer = ProjectTechnologySerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def remove_project_technology(request):
    user = request.user

    # Only Admins and Managers can remove technologies
    if not (is_admin(user) or is_manager(user)):
        return Response(
            {'error': 'Only Admins and Managers can remove technologies from projects.'},
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = RemoveProjectTechnologySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Technology removed from project.'}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def list_projects_with_details(request):
    projects = Project.objects.filter(deleted_at__isnull=True).select_related('created_by', 'manager')
    serializer = ProjectDetailedSerializer(projects, many=True)
    return Response(serializer.data)

