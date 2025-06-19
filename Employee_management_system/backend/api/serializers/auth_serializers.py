from rest_framework import serializers
from api.models import User, Role, UserRole
from django.contrib.auth import authenticate, get_user_model

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


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = '__all__'
