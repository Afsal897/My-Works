from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db import transaction
from api.models import EmployeeProfile, Resignation
from api.serializers import ResignationSerializer
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@transaction.atomic
def submit_resignation(request):
    try:
        employee = EmployeeProfile.objects.get(user=request.user)
    except EmployeeProfile.DoesNotExist:
        return Response({"error": "Employee profile not found."}, status=status.HTTP_404_NOT_FOUND)

    # Check if a resignation already exists and is not deleted
    if Resignation.objects.filter(employee=employee, deleted_at__isnull=True, status='pending').exists():
        return Response({"error": "You already have a pending resignation request."}, status=status.HTTP_400_BAD_REQUEST)

    #setting notice period as 3 months
    serializer = ResignationSerializer(data=request.data)
    if serializer.is_valid():
        start_date = now().date()
        end_date = start_date + relativedelta(months=3)
        serializer.save(employee=employee, start_date=start_date, end_date=end_date)
        return Response({"message": "Resignation request submitted successfully."}, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

