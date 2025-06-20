from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db import transaction
from api.utils import is_manager
from api.models import EmployeeProfile, Project, ProjectAssignment
from api.serializers import PerformanceRatingSerializer, TeammateFeedbackSerializer
from django.utils.timezone import now


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@transaction.atomic
def submit_performance_rating(request):
    user = request.user

    if not is_manager(user):
        return Response({"error": "Only managers can submit performance ratings."}, status=403)

    employee_id = request.data.get("employee")
    try:
        employee = EmployeeProfile.objects.get(id=employee_id)
    except EmployeeProfile.DoesNotExist:
        return Response({"error": "Employee not found."}, status=404)

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
        return Response({"message": "Performance rating submitted."}, status=201)
    return Response(serializer.errors, status=400)


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@transaction.atomic
def submit_teammate_feedback(request):
    try:
        from_employee = EmployeeProfile.objects.get(user=request.user)
    except EmployeeProfile.DoesNotExist:
        return Response({"error": "Employee profile not found."}, status=404)

    to_employee_id = request.data.get("to_employee")
    project_id = request.data.get("project")

    # Validate to_employee exists
    try:
        to_employee = EmployeeProfile.objects.get(id=to_employee_id)
    except EmployeeProfile.DoesNotExist:
        return Response({"error": "Recipient employee not found."}, status=404)

    #both employees are assigned to the same project
    is_valid_pair = ProjectAssignment.objects.filter(
        employee=from_employee, project_id=project_id
    ).exists() and ProjectAssignment.objects.filter(
        employee=to_employee, project_id=project_id
    ).exists()

    if not is_valid_pair:
        return Response({"error": "Both employees must be part of the same project."}, status=403)

    # Serialize & save
    serializer = TeammateFeedbackSerializer(data=request.data)
    if serializer.is_valid():
        status_value = serializer.validated_data.get("status")
        submitted_on = now() if status_value == "submitted" else None
        serializer.save(from_employee=from_employee, submitted_on=submitted_on)
        return Response({"message": "Feedback submitted."}, status=201)
    
    return Response(serializer.errors, status=400)