from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'advertisement', 'contractor', 'author', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('advertisement__title', 'contractor__username', 'author__username', 'comment')
