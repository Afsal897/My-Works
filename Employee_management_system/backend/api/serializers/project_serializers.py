from rest_framework import serializers
from api.models import Project, ProjectAssignment, ProjectTechnology

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'

class ProjectAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectAssignment
        fields = '__all__'

class ProjectTechnologySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectTechnology
        fields = '__all__'
