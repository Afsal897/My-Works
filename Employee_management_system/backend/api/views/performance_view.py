from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db import transaction
from api.utils import is_manager
from api.models import EmployeeProfile, Project, ProjectAssignment
from api.serializers import (
    PerformanceRatingSerializer, 
    TeammateFeedbackSerializer, 
    EditPerformanceRatingSerializer, 
    DeletePerformanceRatingSerializer,
    EditTeammateFeedbackSerializer,
    DeleteTeammateFeedbackSerializer
    )
from django.utils.timezone import now
from rest_framework import status


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@transaction.atomic
def submit_performance_rating(request):
    user = request.user

    if not is_manager(user):
        return Response({"error": "Only managers can submit performance ratings."}, status=status.HTTP_403_FORBIDDEN)

    employee_id = request.data.get("employee")
    try:
        employee = EmployeeProfile.objects.get(id=employee_id)
    except EmployeeProfile.DoesNotExist:
        return Response({"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)

    #Filter completed projects managed by this manager
    manager_completed_projects = Project.objects.filter(manager=user, status="completed")

    #Check if the employee is assigned to any of these completed projects
    if not ProjectAssignment.objects.filter(employee=employee, project__in=manager_completed_projects).exists():
        return Response({
            "error": "You can only rate employees assigned to your completed projects."
        }, status=403)
    
    #Create rating
    serializer = PerformanceRatingSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(rated_by=user)
        return Response({"message": "Performance rating submitted."}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def edit_performance_rating(request):
    user = request.user

    serializer = EditPerformanceRatingSerializer(data=request.data, context={'user': user})
    if serializer.is_valid():
        updated_rating = serializer.save()
        return Response(EditPerformanceRatingSerializer(updated_rating).data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_performance_rating(request):
    user = request.user

    serializer = DeletePerformanceRatingSerializer(data=request.data, context={'user': user})
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Performance rating deleted."}, status=status.HTTP_204_NO_CONTENT)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@transaction.atomic
def submit_teammate_feedback(request):
    try:
        from_employee = EmployeeProfile.objects.get(user=request.user)
    except EmployeeProfile.DoesNotExist:
        return Response({"error": "Employee profile not found."}, status=status.HTTP_404_NOT_FOUND)

    to_employee_id = request.data.get("to_employee")
    project_id = request.data.get("project")

    # Validate to_employee exists
    try:
        to_employee = EmployeeProfile.objects.get(id=to_employee_id)
    except EmployeeProfile.DoesNotExist:
        return Response({"error": "Recipient employee not found."}, status=status.HTTP_404_NOT_FOUND)

    #both employees are assigned to the same project
    is_valid_pair = ProjectAssignment.objects.filter(
        employee=from_employee, project_id=project_id
    ).exists() and ProjectAssignment.objects.filter(
        employee=to_employee, project_id=project_id
    ).exists()

    if not is_valid_pair:
        return Response({"error": "Both employees must be part of the same project."}, status=status.HTTP_403_FORBIDDEN)

    # Serialize & save
    serializer = TeammateFeedbackSerializer(data=request.data)
    if serializer.is_valid():
        status_value = serializer.validated_data.get("status")
        submitted_on = now() if status_value == "submitted" else None
        serializer.save(from_employee=from_employee, submitted_on=submitted_on)
        return Response({"message": "Feedback submitted."}, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def edit_teammate_feedback(request):
    user = request.user

    serializer = EditTeammateFeedbackSerializer(data=request.data, context={'user': user})
    if serializer.is_valid():
        feedback = serializer.save()
        return Response(EditTeammateFeedbackSerializer(feedback).data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_teammate_feedback(request):
    user = request.user

    serializer = DeleteTeammateFeedbackSerializer(data=request.data, context={'user': user})
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Feedback deleted."}, status=status.HTTP_204_NO_CONTENT)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

