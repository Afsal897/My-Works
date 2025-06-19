from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from api.utils import is_admin, is_manager
from api.models import Skill, EmployeeSkill
from api.serializers import SkillSerializer, EmployeeSkillSerializer


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
        return Response({'error': f'Skill "{skill_name}" already exists.'}, status=status.HTTP_400_BAD_REQUEST)
    print("no dup")
    serializer = SkillSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    print(serializer.data)

    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


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