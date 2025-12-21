from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class IdentifierTokenObtainPairSerializer(TokenObtainPairSerializer):
    """JWT login with username OR email OR phone.

    Request example:
    {
      "identifier": "user@example.com",
      "password": "..."
    }
    """

    identifier = serializers.CharField(write_only=True)

    def validate(self, attrs):
        identifier = attrs.get('identifier')
        password = attrs.get('password')
        if not identifier or not password:
            raise serializers.ValidationError('identifier and password are required')

        user = User.objects.filter(
            Q(username__iexact=identifier) | Q(email__iexact=identifier) | Q(phone__iexact=identifier)
        ).first()
        if user is None or not user.check_password(password):
            raise serializers.ValidationError('Invalid credentials')
        if not user.is_active:
            raise serializers.ValidationError('User is disabled')

        data = super().validate({'username': user.username, 'password': password})
        data['user'] = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'phone': user.phone,
            'roles': list(user.roles.values_list('name', flat=True)),
        }
        return data
