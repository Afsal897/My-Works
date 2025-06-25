from rest_framework import serializers
from api.models import Timesheet

class TimesheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timesheet
        fields = '__all__'


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
