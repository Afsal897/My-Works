from rest_framework import serializers
from api.models import User, Role, UserRole
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from api.utils import is_admin

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password',
                   'confirm_password','is_active', 'is_staff',
                      'is_superuser', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True},
            'is_staff': {'read_only': True},
            'is_superuser': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')  
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password']
        )


class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        identifier = data['identifier']
        password = data['password']

        user = None

        # Try username login
        from django.contrib.auth import authenticate
        from api.models import User, EmployeeProfile

        try:
            user_obj = User.objects.get(username=identifier)
            user = authenticate(username=user_obj.username, password=password)
        except User.DoesNotExist:
            try:
                emp = EmployeeProfile.objects.get(id=identifier)
                user = authenticate(username=emp.user.username, password=password)
            except EmployeeProfile.DoesNotExist:
                pass

        if not user:
            raise serializers.ValidationError("Invalid login credentials.")
        
        if not user.is_active:
            raise serializers.ValidationError("User is disabled.")

        data['user'] = user
        return data


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "New passwords do not match."})
        return data


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = '__all__'


class ChangeUserRoleSerializer(serializers.Serializer):
    role_id = serializers.IntegerField()
    user_id = serializers.IntegerField()

    def validate(self, data):
        user_id=data["user_id"]
        role_id=data["role_id"]

        if not User.objects.filter(id=user_id).exists():
            raise serializers.ValidationError("User does not exist")
        
        if not Role.objects.filter(id=role_id).exists():
            raise serializers.ValidationError("Role does not exist")
        
        role = Role.objects.get(id=role_id)
        if role.name.lower() == "admin":
            raise serializers.ValidationError("Cannot assign admin role")
        
        user = User.objects.get(id=user_id)
        if is_admin(user):
            raise serializers.ValidationError("Cannot change role of an Admin user.")

        return data
    
    def save(self, **kwargs):
        user_id = self.validated_data["user_id"]
        role_id = self.validated_data["role_id"]

        try:
            user_role = UserRole.objects.get(user_id=user_id)
        except UserRole.DoesNotExist:
            raise serializers.ValidationError("User does not have a role to change.")

        user_role.role_id = role_id
        user_role.assigned_at = now()
        user_role.save()

        return user_role
    

class DeleteUserSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()

    def validate_user_id(self, value):
        try:
            user = User.objects.get(id=value, deleted_at__isnull=True)
        except User.DoesNotExist:
            raise serializers.ValidationError("user does not exist or is already deleted")
        if is_admin(user):
            raise serializers.ValidationError("Admin accounts cannot be deleted via this route.")
        return value
    
    def save(self, **kwargs):
        user_id = self.validate_user_id['user_id']
        user = User.objects.get(id=user_id)
        user.deleted_at = now()
        user.is_active = False
        user.save()
        return user
    

class UserWithRoleSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_active', 'created_at', 'updated_at', 'role']

    def get_role(self, obj):
        try:
            user_role = UserRole.objects.get(user=obj)
            return RoleSerializer(user_role.role).data
        except UserRole.DoesNotExist:
            return None

