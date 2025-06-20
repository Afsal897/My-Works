from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db import transaction
from django.utils.timezone import now
from api.models import EmployeeProfile, Payroll
from api.serializers import TimesheetSerializer
from decimal import Decimal


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@transaction.atomic
def submit_timesheet(request):
    user = request.user

    try:
        employee = EmployeeProfile.objects.get(user=user)
    except EmployeeProfile.DoesNotExist:
        return Response({"error": "Employee profile not found."}, status=status.HTTP_404_NOT_FOUND)

    entries = request.data

    if not isinstance(entries, list):
        return Response({"error": "Expected a list of timesheet entries."}, status=status.HTTP_400_BAD_REQUEST)

    created_entries = []
    for entry in entries:
        entry_data = {
            "employee": employee.id,
            "project": entry.get("project"),
            "date": entry.get("date"),
            "work_description": entry.get("work_description"),
            "hours_worked": entry.get("hours_worked"),
            "submitted_on": now()
        }
        serializer = TimesheetSerializer(data=entry_data)
        if not serializer.is_valid():
            # Rollback entire batch on any error
            return Response({"error": "Validation failed", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        created_entries.append(serializer)

    # All validated, now save them
    for serializer in created_entries:
        serializer.save()

    return Response({"message": f"{len(created_entries)} timesheet entries submitted successfully."}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@transaction.atomic
def add_payroll(request):
    data = request.data
    try:
        employee = EmployeeProfile.objects.get(id=data.get("employee_id"))
    except EmployeeProfile.DoesNotExist:
        return Response({"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)

    try:
        basic_salary = Decimal(data["basic_salary"])
        allowances = Decimal(data["allowances"])
        deductions = Decimal(data["deductions"])
    except KeyError as e:
        return Response({"error": f"Missing field: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception:
        return Response({"error": "Invalid data format."}, status=status.HTTP_400_BAD_REQUEST)

    net_pay = basic_salary + allowances - deductions

    payroll = Payroll.objects.create(
        employee=employee,
        basic_salary=basic_salary,
        allowances=allowances,
        deductions=deductions,
        net_pay=net_pay,
        processed_by=request.user
    )

    return Response({
        "message": "Payroll added successfully.",
        "payroll_id": payroll.id,
        "net_pay": float(net_pay)
    }, status=status.HTTP_201_CREATED)