from rest_framework.decorators import permission_classes, api_view, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from api.serializers import DepartmentSerializer, EmployeeProfileSerializer
from api.models import Department
from api.utils import is_admin


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
    
    serializer=EmployeeProfileSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)