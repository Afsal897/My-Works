from rest_framework import serializers
from api.models import PerformanceRating, TeammateFeedback

class PerformanceRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceRating
        fields = '__all__'

class TeammateFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeammateFeedback
        fields = '__all__'
