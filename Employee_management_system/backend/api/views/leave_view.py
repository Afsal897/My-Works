from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication

from api.models import EmployeeProfile
from api.serializers import LeaveSerializer, LeaveActionSerializer
from datetime import datetime
from api.utils import is_admin, is_manager


#leave balace is set in auth_view inside employee registration
@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def submit_leave_request(request):
    user = request.user

    # Ensure employee profile exists
    try:
        employee = EmployeeProfile.objects.get(user=user)
    except EmployeeProfile.DoesNotExist:
        return Response({'error': 'Employee profile not found.'}, status=status.HTTP_404_NOT_FOUND)

    data = request.data.copy()
    data['employee'] = employee.id
    data['requested_on'] = datetime.now()

    serializer = LeaveSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def approve_leave(request):
    if not (is_admin(request.user) or is_manager(request.user)):
        return Response({"error": "Only Admins or Managers can approve leaves."}, status=status.HTTP_403_FORBIDDEN)

    serializer = LeaveActionSerializer(data=request.data)
    if serializer.is_valid():
        leave = serializer.approve(request.user)
        return Response({
            "message": "Leave approved.",
            "leave_id": leave.id,
            "is_lop": leave.is_lop,
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def reject_leave(request):
    if not (is_admin(request.user) or is_manager(request.user)):
        return Response({"error": "Only Admins or Managers can reject leaves."}, status=status.HTTP_403_FORBIDDEN)

    serializer = LeaveActionSerializer(data=request.data)
    if serializer.is_valid():
        leave = serializer.reject(request.user)
        return Response({
            "message": "Leave rejected.",
            "leave_id": leave.id
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)