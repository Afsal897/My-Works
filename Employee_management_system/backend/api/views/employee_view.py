from rest_framework.decorators import permission_classes, api_view, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from api.serializers import (
    DepartmentSerializer, 
    EmployeeProfileSerializer, 
    DeleteDepartmentSerializer,
    DesignationSerializer,
    UnassignedEmployeeSerializer
)
from api.models import Department, EmployeeProfile, Designation, ProjectAssignment
from api.utils import is_admin, is_manager


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_department(request):
    if not is_admin(request.user):
        return Response({'error': 'Only Admins are allowed to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
    department_name = request.data.get('name', '').strip()

    #Check for duplicate department name (case-insensitive)
    if Department.objects.filter(name__iexact=department_name, deleted_at__isnull=True).exists():
        return Response({'error': f'Department "{department_name}" already exists.'}, status=status.HTTP_400_BAD_REQUEST)

    serializer=DepartmentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_employee_profile(request):
    if not is_admin(request.user):
        return Response({'error': 'Only Admins are allowed to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = EmployeeProfileSerializer(data=request.data)
    if serializer.is_valid():
        employee_profile = serializer.save()  # Save and get the instance

        return Response(EmployeeProfileSerializer(employee_profile).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_designation(request):
    user = request.user
    if not is_admin(user):
        return Response({"error": "Only Admins can create designations."}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = DesignationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Designation created successfully."}, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def edit_department(request):
    user = request.user
    if not is_admin(user):
        return Response({"error": "User does not have permission."}, status=status.HTTP_403_FORBIDDEN)

    department_id = request.data.get("department_id")
    if not department_id:
        return Response({"error": "Department ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        department = Department.objects.get(id=department_id, deleted_at__isnull=True)
    except Department.DoesNotExist:
        return Response({"error": "Department does not exist."}, status=status.HTTP_404_NOT_FOUND)

    serializer = DepartmentSerializer(department, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Department updated successfully."}, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_department(request):
    if not is_admin(request.user):
        return Response({"error": "Only Admins can delete departments."}, status=status.HTTP_403_FORBIDDEN)

    serializer = DeleteDepartmentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Department soft-deleted successfully."}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PATCH"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def edit_employee_profile(request):
    if not is_admin(request.user):
        return Response({"error": "Only Admins can edit employee profiles."}, status=status.HTTP_403_FORBIDDEN)

    employee_id = request.data.get("employee_id")
    if not employee_id:
        return Response({"error": "Employee ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        profile = EmployeeProfile.objects.get(id=employee_id, deleted_at__isnull=True)
    except EmployeeProfile.DoesNotExist:
        return Response({"error": "Employee profile not found."}, status=status.HTTP_404_NOT_FOUND)

    #Validate field names
    allowed_fields = set(EmployeeProfileSerializer().get_fields().keys()) | {"employee_id"}
    invalid_fields = [key for key in request.data.keys() if key not in allowed_fields]

    if invalid_fields:
        return Response({
            "error": "Invalid field(s) in request.",
            "invalid_fields": invalid_fields
        }, status=status.HTTP_400_BAD_REQUEST)

    serializer = EmployeeProfileSerializer(profile, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Employee profile updated successfully."}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def list_departments(request):
    departments = Department.objects.filter(deleted_at__isnull=True).select_related('head', 'head__user')
    serializer = DepartmentSerializer(departments, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def list_designations(request):
    designations = Designation.objects.filter(deleted_at__isnull=True).order_by('title')
    serializer = DesignationSerializer(designations, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def list_employees(request):
    employees = EmployeeProfile.objects.filter(deleted_at__isnull=True).select_related('department', 'designation', 'user')
    serializer = EmployeeProfileSerializer(employees, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def list_unassigned_employees(request):
    user = request.user

    if not (is_admin(user) or is_manager(user)):
        return Response({'error': 'Only Admins and Managers can view this list.'}, status=status.HTTP_403_FORBIDDEN)

    # Get IDs of employees who are currently assigned to active projects
    assigned_employee_ids = ProjectAssignment.objects.filter(
        assignment_status='active',
        deleted_at__isnull=True
    ).values_list('employee_id', flat=True).distinct()

    # Fetch all employees NOT in the assigned list
    unassigned_employees = EmployeeProfile.objects.exclude(id__in=assigned_employee_ids)

    serializer = UnassignedEmployeeSerializer(unassigned_employees, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
