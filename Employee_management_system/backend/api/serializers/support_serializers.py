from rest_framework import serializers
from api.models import Resignation, SupportRequest, Notification

class ResignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resignation
        fields = '__all__'

class SupportRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportRequest
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
