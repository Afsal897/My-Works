from api.models import UserRole

def is_admin(user):
    try:
        return user and UserRole.objects.get(user=user).role.name.lower() == 'admin'
    except UserRole.DoesNotExist:
        return False

def is_manager(user):
    try:
        return user and UserRole.objects.get(user=user).role.name.lower() == 'manager'
    except UserRole.DoesNotExist:
        return False
