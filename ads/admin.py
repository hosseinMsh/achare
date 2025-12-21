from django.contrib import admin

from .models import Advertisement, JobRequest


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status', 'customer', 'contractor', 'created_at')
    list_filter = ('status', 'category')
    search_fields = ('title', 'description', 'customer__username', 'contractor__username')


@admin.register(JobRequest)
class JobRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'advertisement', 'contractor', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('advertisement__title', 'contractor__username')
