from rest_framework import serializers
from api.models import PerformanceRating, TeammateFeedback
from django.utils.timezone import now
from api.utils import is_admin

class PerformanceRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceRating
        fields = ['employee', 'rating', 'review_comment', 'review_date']

class TeammateFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeammateFeedback
        fields = ['to_employee', 'project', 'feedback_text', 'rating', 'status']

class EditPerformanceRatingSerializer(serializers.ModelSerializer):
    rating_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = PerformanceRating
        fields = ['rating_id', 'rating', 'review_comment', 'review_date']

    def validate_rating_id(self, value):
        user = self.context['user']
        try:
            rating = PerformanceRating.objects.get(id=value, rated_by=user, deleted_at__isnull=True)
        except PerformanceRating.DoesNotExist:
            raise serializers.ValidationError("Performance rating not found or not authorized to edit.")
        return value

    def update_instance(self):
        """Get and return the instance after validation"""
        return PerformanceRating.objects.get(id=self.validated_data['rating_id'])

    def save(self, **kwargs):
        rating = self.update_instance()
        rating.rating = self.validated_data.get('rating', rating.rating)
        rating.review_comment = self.validated_data.get('review_comment', rating.review_comment)
        rating.review_date = self.validated_data.get('review_date', rating.review_date)
        rating.save()
        return rating

class DeletePerformanceRatingSerializer(serializers.Serializer):
    rating_id = serializers.IntegerField()

    def validate_rating_id(self, value):
        user = self.context['user']
        try:
            rating = PerformanceRating.objects.get(id=value, deleted_at__isnull=True)
        except PerformanceRating.DoesNotExist:
            raise serializers.ValidationError("Rating not found or already deleted.")
        
        if not is_admin(user) and rating.rated_by != user:
            raise serializers.ValidationError("You are not allowed to delete this rating.")

        self.instance = rating
        return value

    def save(self, **kwargs):
        self.instance.deleted_at = now()
        self.instance.save()
        return self.instance

class EditTeammateFeedbackSerializer(serializers.ModelSerializer):
    feedback_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = TeammateFeedback
        fields = ['feedback_id', 'feedback_text', 'rating', 'status', 'submitted_on']

    def validate_feedback_id(self, value):
        from api.utils import is_admin
        user = self.context['user']
        try:
            feedback = TeammateFeedback.objects.get(id=value, deleted_at__isnull=True)
        except TeammateFeedback.DoesNotExist:
            raise serializers.ValidationError("Feedback not found.")

        # Only admin or sender can edit
        if not is_admin(user) and feedback.from_employee.user != user:
            raise serializers.ValidationError("You are not authorized to edit this feedback.")

        self.instance = feedback
        return value

    def save(self, **kwargs):
        feedback = self.instance
        feedback.feedback_text = self.validated_data.get('feedback_text', feedback.feedback_text)
        feedback.rating = self.validated_data.get('rating', feedback.rating)
        feedback.status = self.validated_data.get('status', feedback.status)
        feedback.submitted_on = self.validated_data.get('submitted_on', feedback.submitted_on)
        feedback.save()
        return feedback

class DeleteTeammateFeedbackSerializer(serializers.Serializer):
    feedback_id = serializers.IntegerField()

    def validate_feedback_id(self, value):
        from api.utils import is_admin
        user = self.context['user']
        try:
            feedback = TeammateFeedback.objects.get(id=value, deleted_at__isnull=True)
        except TeammateFeedback.DoesNotExist:
            raise serializers.ValidationError("Feedback not found or already deleted.")

        if not is_admin(user) and feedback.from_employee.user != user:
            raise serializers.ValidationError("You are not authorized to delete this feedback.")

        self.instance = feedback
        return value

    def save(self, **kwargs):
        self.instance.deleted_at = now()
        self.instance.save()
        return self.instance
