from rest_framework import serializers
from api.models import Resignation, Notification
from django.utils.timezone import now


class ResignationSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.user.username", read_only=True)

    class Meta:
        model = Resignation
        fields = ['id', 'employee', 'employee_name', 'start_date', 'end_date', 'reason', 'status', 'created_at', 'updated_at']

class WithdrawResignationSerializer(serializers.Serializer):
    resignation_id = serializers.IntegerField()

    def validate_resignation_id(self, value):
        user = self.context['user']
        try:
            resignation = Resignation.objects.get(id=value, deleted_at__isnull=True)
        except Resignation.DoesNotExist:
            raise serializers.ValidationError("Resignation not found or already withdrawn.")

        # Only the employee who submitted can withdraw if status is pending
        if resignation.status != 'pending':
            raise serializers.ValidationError("Only pending resignations can be withdrawn.")

        if resignation.employee.user != user:
            raise serializers.ValidationError("You are not authorized to withdraw this resignation.")

        self.instance = resignation
        return value

    def save(self, **kwargs):
        self.instance.deleted_at = now()
        self.instance.save()
        return self.instance


class NotificationSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'event_type', 'related_entity_id',
            'sender', 'sender_username', 'is_read',
            'created_at', 'updated_at'
        ]

