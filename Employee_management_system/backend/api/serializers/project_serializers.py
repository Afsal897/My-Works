from rest_framework import serializers
from api.models import Project, ProjectAssignment, ProjectTechnology, EmployeeProfile, Skill
from django.utils.timezone import now
from api.utils import is_admin


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class EditProjectSerializer(serializers.ModelSerializer):
    project_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Project
        fields = ['project_id', 'name', 'description', 'start_date', 'end_date', 'status', 'manager']

    def validate_project_id(self, value):
        
        user = self.context['user']
        try:
            project = Project.objects.get(id=value, deleted_at__isnull=True)
        except Project.DoesNotExist:
            raise serializers.ValidationError("Project not found.")

        if not is_admin(user):
            raise serializers.ValidationError("Only admins can edit projects.")

        self.instance = project
        return value

    def save(self, **kwargs):
        project = self.instance
        for field in ['name', 'description', 'start_date', 'end_date', 'status', 'manager']:
            if field in self.validated_data:
                setattr(project, field, self.validated_data[field])
        project.save()
        return project


class DeleteProjectSerializer(serializers.Serializer):
    project_id = serializers.IntegerField()

    def validate_project_id(self, value):
        
        user = self.context['user']
        try:
            project = Project.objects.get(id=value, deleted_at__isnull=True)
        except Project.DoesNotExist:
            raise serializers.ValidationError("Project not found or already deleted.")

        if not is_admin(user):
            raise serializers.ValidationError("Only admins can delete projects.")

        self.instance = project
        return value

    def save(self, **kwargs):
        self.instance.deleted_at = now()
        self.instance.save()
        return self.instance


class ProjectAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectAssignment
        fields = '__all__'


class RemoveProjectAssignmentSerializer(serializers.Serializer):
    project_id = serializers.IntegerField()
    employee_id = serializers.IntegerField()

    def validate(self, data):
        from api.utils import is_admin
        user = self.context['user']
        try:
            assignment = ProjectAssignment.objects.get(
                project_id=data['project_id'],
                employee_id=data['employee_id'],
                deleted_at__isnull=True,
                assignment_status='active'
            )
        except ProjectAssignment.DoesNotExist:
            raise serializers.ValidationError("Assignment not found or already removed.")

        # Only admins or the person who assigned can remove
        if not is_admin(user) and assignment.assigned_by != user:
            raise serializers.ValidationError("You are not authorized to remove this assignment.")

        self.instance = assignment
        return data

    def save(self, **kwargs):
        self.instance.assignment_status = 'removed'
        self.instance.deleted_at = now()
        self.instance.save()
        return self.instance


class ProjectTechnologySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectTechnology
        fields = '__all__'


class RemoveProjectTechnologySerializer(serializers.Serializer):
    project_id = serializers.IntegerField()
    skill_id = serializers.IntegerField()

    def validate(self, data):
        try:
            tech = ProjectTechnology.objects.get(
                project_id=data['project_id'],
                skill_id=data['skill_id'],
                deleted_at__isnull=True
            )
        except ProjectTechnology.DoesNotExist:
            raise serializers.ValidationError("This technology is not assigned to the project or already removed.")

        self.instance = tech
        return data

    def save(self, **kwargs):
        self.instance.deleted_at = now()
        self.instance.save()
        return self.instance


class AssignedEmployeeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = EmployeeProfile
        fields = ['id', 'name', 'designation']


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name']


class ProjectDetailedSerializer(serializers.ModelSerializer):
    assigned_people = serializers.SerializerMethodField()
    technologies = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'start_date', 'end_date',
            'status', 'created_by', 'manager',
            'assigned_people', 'technologies'
        ]

    def get_assigned_people(self, obj):
        assignments = ProjectAssignment.objects.filter(
            project=obj,
            assignment_status='active',
            deleted_at__isnull=True
        ).select_related('employee__user', 'employee__designation')
        employees = [a.employee for a in assignments]
        return AssignedEmployeeSerializer(employees, many=True).data

    def get_technologies(self, obj):
        techs = ProjectTechnology.objects.filter(
            project=obj,
            deleted_at__isnull=True
        ).select_related('skill')
        skills = [t.skill for t in techs]
        return SkillSerializer(skills, many=True).data


class CompleteProjectSerializer(serializers.Serializer):
    project_id = serializers.IntegerField()

    def validate_project_id(self, value):
        try:
            project = Project.objects.get(id=value, deleted_at__isnull=True)
        except Project.DoesNotExist:
            raise serializers.ValidationError("Project not found.")

        self.instance = project
        return value

    def save(self, **kwargs):
        project = self.instance
        project.status = "completed"
        project.save()

        # Mark all active assignments as completed and soft-delete
        ProjectAssignment.objects.filter(
            project=project,
            assignment_status='active',
            deleted_at__isnull=True
        ).update(
            assignment_status='completed',
            deleted_at=now()
        )

        return project
