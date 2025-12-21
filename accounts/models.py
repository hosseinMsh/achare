from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.Model):
    """A dynamic role model to allow future extension without code changes."""

    name = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        return self.name


class User(AbstractUser):
    """Custom user model.

    Requirements from assignment:
    - User can login via username/email/phone.
    - Users have roles (customer/contractor/support/admin).

    We model roles dynamically (ManyToMany) to support the optional part (dynamic access).
    """

    phone = models.CharField(max_length=20, blank=True)
    roles = models.ManyToManyField(Role, related_name='users', blank=True)

    def has_role(self, role_name: str) -> bool:
        return self.roles.filter(name=role_name).exists()
