from rest_framework import serializers
from api.models import Resignation, Notification

class ResignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resignation
        fields = ['start_date', 'end_date', 'reason']
        read_only_fields = ['start_date', 'end_date']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'recipient', 'event_type', 'related_entity_id', 'is_read']
        read_only_fields = ['is_read']
