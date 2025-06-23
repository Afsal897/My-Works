from rest_framework import serializers
from api.models import EmployeeProfile, Department
from django.utils.timezone import now

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'head']


class EmployeeProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeProfile
        fields = '__all__'


class DeleteDepartmentSerializer(serializers.Serializer):
    department_id = serializers.IntegerField()

    def validate_department_id(self, value):
        try:
            department = Department.objects.get(id=value, deleted_at__isnull=True)
        except Department.DoesNotExist:
            raise serializers.ValidationError("Department not found or already deleted.")
        return value
    
    def save(self, **kwargs):
        department = Department.objects.get(id=self.validated_data["department_id"])
        department.deleted_at = now()
        department.save()
        return department