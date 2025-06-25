from rest_framework import serializers
from api.models import Skill, EmployeeSkill
from django.utils.timezone import now

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'

class EditSkillSerializer(serializers.ModelSerializer):
    skill_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Skill
        fields = ['skill_id', 'name']

    def validate_skill_id(self, value):
        try:
            skill = Skill.objects.get(id=value, deleted_at__isnull=True)
        except Skill.DoesNotExist:
            raise serializers.ValidationError("Skill not found or already deleted.")
        self.instance = skill
        return value

    def validate_name(self, value):
        if Skill.objects.filter(name=value, deleted_at__isnull=True).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("A skill with this name already exists.")
        return value

    def save(self, **kwargs):
        self.instance.name = self.validated_data['name']
        self.instance.save()
        return self.instance

class DeleteSkillSerializer(serializers.Serializer):
    skill_id = serializers.IntegerField()

    def validate_skill_id(self, value):
        try:
            skill = Skill.objects.get(id=value, deleted_at__isnull=True)
        except Skill.DoesNotExist:
            raise serializers.ValidationError("Skill not found or already deleted.")
        self.instance = skill
        return value

    def save(self, **kwargs):
        self.instance.deleted_at = now()
        self.instance.save()
        return self.instance

class EmployeeSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeSkill
        fields = '__all__'

class RemoveEmployeeSkillSerializer(serializers.Serializer):
    employee_id = serializers.IntegerField()
    skill_id = serializers.IntegerField()

    def validate(self, data):
        try:
            record = EmployeeSkill.objects.get(
                employee_id=data['employee_id'],
                skill_id=data['skill_id'],
                deleted_at__isnull=True
            )
        except EmployeeSkill.DoesNotExist:
            raise serializers.ValidationError("Skill not assigned or already removed.")

        self.instance = record
        return data

    def save(self, **kwargs):
        self.instance.deleted_at = now()
        self.instance.save()
        return self.instance
