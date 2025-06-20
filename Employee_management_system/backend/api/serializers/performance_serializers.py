from rest_framework import serializers
from api.models import PerformanceRating, TeammateFeedback

class PerformanceRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceRating
        fields = ['employee', 'rating', 'review_comment', 'review_date']

class TeammateFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeammateFeedback
        fields = ['to_employee', 'project', 'feedback_text', 'rating', 'status']
