from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from api.utils import is_admin, is_manager
from api.models import Skill, EmployeeSkill, EmployeeProfile
from api.serializers import (
    SkillSerializer, 
    EmployeeSkillSerializer,
    EditSkillSerializer,
    DeleteSkillSerializer,
    RemoveEmployeeSkillSerializer
    )


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_skill(request):
    if not (is_admin(request.user) or is_manager(request.user)):
        return Response({'error': 'Only Admins and Managers are allowed to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
    skill_name = request.data.get("name", "").strip()
    print("duplicate")
    # Check for duplicate skill
    if Skill.objects.filter(name__iexact=skill_name, deleted_at__isnull=True).exists():
        return Response({'error': f'Skill "{skill_name}" already exists.'}, 
                        status=status.HTTP_400_BAD_REQUEST)
    print("no dup")
    serializer = SkillSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    print(serializer.data)

    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def edit_skill(request):
    user = request.user

    if not is_admin(user):
        return Response({'error': 'Only admins can edit skills.'}, 
                        status=status.HTTP_403_FORBIDDEN)

    serializer = EditSkillSerializer(data=request.data, context={'user': user})
    if serializer.is_valid():
        updated_skill = serializer.save()
        return Response(EditSkillSerializer(updated_skill).data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_skill(request):
    user = request.user

    if not is_admin(user):
        return Response({'error': 'Only admins can delete skills.'}, 
                        status=status.HTTP_403_FORBIDDEN)

    serializer = DeleteSkillSerializer(data=request.data, context={'user': user})
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Skill deleted successfully.'}, 
                        status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def add_employee_skill(request):
    data = request.data.copy()

    # Normalize input
    employee_id = data.get('employee')
    skill_id = data.get('skill')

    # Uniqueness Check
    if EmployeeSkill.objects.filter(employee_id=employee_id, skill_id=skill_id, deleted_at__isnull=True).exists():
        return Response(
            {"error": "This employee already has the specified skill assigned."},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = EmployeeSkillSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def remove_employee_skill(request):
    serializer = RemoveEmployeeSkillSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Employee skill deleted successfully."}, 
                        status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def list_all_skills(request):
    skills = Skill.objects.filter(deleted_at__isnull=True)
    serializer = SkillSerializer(skills, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def list_employee_skills(request):
    user = request.user

    try:
        employee = EmployeeProfile.objects.get(user=user)
    except EmployeeProfile.DoesNotExist:
        return Response({"error": "Employee profile not found."}, status=404)

    # Admins and Managers can see all employee skills
    if is_admin(user) or is_manager(user):
        skills = EmployeeSkill.objects.filter(deleted_at__isnull=True)
    else:
        # Regular employees can only see their own skills
        skills = EmployeeSkill.objects.filter(employee=employee, deleted_at__isnull=True)

    serializer = EmployeeSkillSerializer(skills, many=True)
    return Response(serializer.data)

