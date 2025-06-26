from rest_framework import serializers
from api.models import EmployeeProfile, Department, Designation
from django.utils.timezone import now


class DepartmentSerializer(serializers.ModelSerializer):
    head_name = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'head', 'head_name', 'created_at', 'updated_at']

    def get_head_name(self, obj):
        return obj.head.user.username if obj.head and obj.head.user else None
    

class DesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = ['id', 'title', 'description']


class EmployeeProfileSerializer(serializers.ModelSerializer):
    designation_title = serializers.CharField(source='designation.title', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = EmployeeProfile
        fields = [
            'id', 'user', 'user_username', 'phone_number', 'date_of_birth',
            'join_date', 'profile_picture', 'supervisor', 'department', 'department_name',
            'designation', 'designation_title', 'created_at', 'updated_at'
        ]


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
    

