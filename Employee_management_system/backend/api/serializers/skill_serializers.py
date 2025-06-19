from rest_framework import serializers
from api.models import Skill, EmployeeSkill

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'

class EmployeeSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeSkill
        fields = '__all__'
