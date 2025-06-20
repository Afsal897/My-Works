from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication

from api.models import EmployeeProfile
from api.serializers import LeaveSerializer
from datetime import datetime

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


