from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .jwt import IdentifierTokenObtainPairSerializer
from .serializers import RegisterSerializer, SetUserRolesSerializer, UserPublicSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer


class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
    serializer_class = IdentifierTokenObtainPairSerializer


class MeView(generics.RetrieveAPIView):
    serializer_class = UserPublicSerializer

    def get_object(self):
        return self.request.user


class IsAdminOrSupport(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.roles.filter(name__in=['admin', 'support']).exists()


class SetUserRolesView(APIView):
    """Set roles for a user (admin/support only)."""

    permission_classes = [IsAdminOrSupport]

    def post(self, request, user_id: int):
        user = generics.get_object_or_404(User, id=user_id)
        serializer = SetUserRolesSerializer(data=request.data, context={'user': user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserPublicSerializer(user).data, status=status.HTTP_200_OK)
