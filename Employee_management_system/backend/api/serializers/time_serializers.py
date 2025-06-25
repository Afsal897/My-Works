from rest_framework import serializers
from api.models import Timesheet
from datetime import date
from api.utils import is_admin


class TimesheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timesheet
        fields = '__all__'

    def validate_date(self, value):
        if value > date.today():
            raise serializers.ValidationError("You cannot submit a timesheet for a future date.")
        return value

    def validate(self, data):
        employee = data.get('employee')
        date_val = data.get('date')

        if Timesheet.objects.filter(
            employee=employee,
            date=date_val,
            deleted_at__isnull=True
        ).exists():
            raise serializers.ValidationError("A timesheet entry for this date already exists.")
        return data


class ApproveRejectTimesheetSerializer(serializers.Serializer):
    timesheet_id = serializers.IntegerField()
    action = serializers.ChoiceField(choices=['approve', 'reject'])

    def validate_timesheet_id(self, value):
        try:
            timesheet = Timesheet.objects.get(id=value, deleted_at__isnull=True)
        except Timesheet.DoesNotExist:
            raise serializers.ValidationError("Timesheet not found or already deleted.")
        self.instance = timesheet
        return value

    def save(self, **kwargs):
        action = self.validated_data['action']
        user = self.context['user']

        self.instance.approved_by = user
        self.instance.is_approved = True if action == 'approve' else False
        self.instance.save()
        return self.instance


class EditTimesheetSerializer(serializers.ModelSerializer):
    timesheet_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Timesheet
        fields = ['timesheet_id', 'project', 'date', 'work_description', 'hours_worked']

    def validate_timesheet_id(self, value):
        user = self.context['user']
        try:
            timesheet = Timesheet.objects.get(id=value, deleted_at__isnull=True)
        except Timesheet.DoesNotExist:
            raise serializers.ValidationError("Timesheet not found or already deleted.")

        # Only owner or admin can edit
        if not is_admin(user) and timesheet.employee.user != user:
            raise serializers.ValidationError("You are not authorized to edit this timesheet.")

        if timesheet.is_approved:
            raise serializers.ValidationError("Approved timesheets cannot be edited.")

        self.instance = timesheet
        return value

    def validate_date(self, value):
        if value > date.today():
            raise serializers.ValidationError("You cannot set a future date.")
        return value

    def validate(self, data):
        # Skip if date not being changed
        if 'date' not in data:
            return data

        employee = self.instance.employee
        new_date = data['date']

        # Check for duplicate (excluding the instance itself)
        if Timesheet.objects.filter(
            employee=employee,
            date=new_date,
            deleted_at__isnull=True
        ).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("A timesheet for this date already exists.")

        return data

    def save(self, **kwargs):
        for field in ['project', 'date', 'work_description', 'hours_worked']:
            if field in self.validated_data:
                setattr(self.instance, field, self.validated_data[field])
        self.instance.save()
        return self.instance

