from rest_framework import serializers
from api.models import Resignation, Notification
from django.utils.timezone import now


class ResignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resignation
        fields = ['start_date', 'end_date', 'reason']
        read_only_fields = ['start_date', 'end_date']

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
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'recipient', 'event_type', 'related_entity_id', 'is_read']
        read_only_fields = ['is_read']


