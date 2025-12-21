from __future__ import annotations

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers

from .models import Role

User = get_user_model()


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']


class UserPublicSerializer(serializers.ModelSerializer):
    roles = RoleSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'first_name', 'last_name', 'roles']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password', 'first_name', 'last_name']

    def validate_password(self, value: str) -> str:
        validate_password(value)
        return value

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        # Default role is customer.
        role, _ = Role.objects.get_or_create(name='customer')
        user.roles.add(role)
        return user


class SetUserRolesSerializer(serializers.Serializer):
    """Admin/Support can set roles for a user."""

    roles = serializers.ListField(
        child=serializers.CharField(max_length=50),
        allow_empty=False,
    )

    def validate_roles(self, roles: list[str]) -> list[str]:
        # Basic validation: unique names, normalized.
        normalized = [r.strip().lower() for r in roles if r.strip()]
        if not normalized:
            raise serializers.ValidationError('roles cannot be empty')
        if len(set(normalized)) != len(normalized):
            raise serializers.ValidationError('roles must be unique')
        return normalized

    def save(self, **kwargs):
        user = self.context['user']
        role_names = self.validated_data['roles']
        role_objs = []
        for name in role_names:
            role, _ = Role.objects.get_or_create(name=name)
            role_objs.append(role)
        user.roles.set(role_objs)
        return user
