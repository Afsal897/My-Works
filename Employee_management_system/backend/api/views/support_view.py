from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db import transaction
from api.models import EmployeeProfile, Resignation, User, Notification
from api.serializers import (
    ResignationSerializer, 
    NotificationSerializer,
    WithdrawResignationSerializer
    )
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta
from api.utils import is_admin, is_manager


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@transaction.atomic
def submit_resignation(request):
    try:
        employee = EmployeeProfile.objects.get(user=request.user)
    except EmployeeProfile.DoesNotExist:
        return Response({"error": "Employee profile not found."}, 
                        status=status.HTTP_404_NOT_FOUND)

    # Check if a resignation already exists and is not deleted
    if Resignation.objects.filter(employee=employee, deleted_at__isnull=True, status='pending').exists():
        return Response({"error": "You already have a pending resignation request."}, 
                        status=status.HTTP_400_BAD_REQUEST)

    #setting notice period as 3 months
    serializer = ResignationSerializer(data=request.data)
    if serializer.is_valid():
        start_date = now().date()
        end_date = start_date + relativedelta(months=3)
        serializer.save(employee=employee, start_date=start_date, end_date=end_date)
        return Response({"message": "Resignation request submitted successfully."}, 
                        status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def withdraw_resignation(request):
    user = request.user
    serializer = WithdrawResignationSerializer(data=request.data, context={'user': user})

    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Resignation withdrawn successfully.'}, 
                        status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#just for understanding what all is needed in notification no real purpose for this api
@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@transaction.atomic
def create_notification(request):
    data = request.data

    try:
        recipient = User.objects.get(id=data.get("recipient_id"))
    except User.DoesNotExist:
        return Response({"error": "Recipient not found."}, 
                        status=status.HTTP_404_NOT_FOUND)

    serializer = NotificationSerializer(data={
        "title": data.get("title"),
        "message": data.get("message"),
        "recipient": recipient.id,
        "event_type": data.get("event_type"),
        "related_entity_id": data.get("related_entity_id")
    })

    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Notification created successfully."}, 
                        status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_my_notifications(request):
    user = request.user
    notifications = Notification.objects.filter(
    recipient=user, deleted_at__isnull=True).order_by('-created_at')

    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def list_resignations(request):
    user = request.user

    # Admins and Managers see all
    if is_admin(user) or is_manager(user):
        resignations = Resignation.objects.filter(deleted_at__isnull=True)
    else:
        try:
            employee_profile = EmployeeProfile.objects.get(user=user)
        except EmployeeProfile.DoesNotExist:
            return Response({"error": "Employee profile not found."}, status=404)

        resignations = Resignation.objects.filter(employee=employee_profile, deleted_at__isnull=True)

    serializer = ResignationSerializer(resignations, many=True)
    return Response(serializer.data)

