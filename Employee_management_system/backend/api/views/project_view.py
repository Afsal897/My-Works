from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from api.serializers import ProjectSerializer
from api.utils import is_admin, is_manager

@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_project(request):
    user = request.user

    # Allow only Admins and Managers
    if not (is_admin(user) or is_manager(user)):
        return Response({'error': 'Only Admins and Managers can create projects.'}, status=status.HTTP_403_FORBIDDEN)

    data = request.data.copy()
    # Automatically assign current user as creator
    data['created_by'] = user.id

    # Validate and save
    serializer = ProjectSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
