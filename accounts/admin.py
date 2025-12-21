from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Role

User = get_user_model()


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'phone', 'is_active', 'is_superuser')
    search_fields = ('username', 'email', 'phone')
    filter_horizontal = ('roles',)
