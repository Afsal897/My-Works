from rest_framework import serializers
from api.models import PerformanceRating, TeammateFeedback
from django.utils.timezone import now
from api.utils import is_admin


class PerformanceRatingSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.username', read_only=True)
    rated_by_name = serializers.CharField(source='rated_by.username', read_only=True)

    class Meta:
        model = PerformanceRating
        fields = [
            'id', 'employee', 'employee_name',
            'rated_by', 'rated_by_name',
            'project', 'rating', 'review_comment', 
            'review_date','created_at', 'updated_at'
        ]


class CreateTeammateFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeammateFeedback
        fields = ['to_employee', 'project', 'feedback_text', 'rating', 'status']

    def validate(self, data):
        from_employee = self.context['from_employee']
        to_employee = data.get("to_employee")
        project = data.get("project")

        # Prevent self-feedback
        if to_employee == from_employee:
            raise serializers.ValidationError("You cannot give feedback to yourself.")

        # Check for duplicate feedback (same from, to, and project)
        if TeammateFeedback.objects.filter(
            from_employee=from_employee,
            to_employee=to_employee,
            project=project,
            deleted_at__isnull=True
        ).exists():
            raise serializers.ValidationError("Feedback already submitted for this teammate in the selected project.")

        return data

    def create(self, validated_data):
        from_employee = self.context['from_employee']
        validated_data['from_employee'] = from_employee
        return TeammateFeedback.objects.create(**validated_data)

class TeammateFeedbackSerializer(serializers.ModelSerializer):
    from_employee_name = serializers.CharField(source='from_employee.user.username', read_only=True)
    to_employee_name = serializers.CharField(source='to_employee.user.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = TeammateFeedback
        fields = [
            'id', 'from_employee', 'from_employee_name',
            'to_employee', 'to_employee_name',
            'project', 'project_name',
            'feedback_text', 'rating', 'status', 'submitted_on',
            'created_at', 'updated_at'
        ]
        

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
