from django.contrib import admin
from .models import CustomUser, UserProfile

# Register your models here.
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('email',)
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    ordering = ('email',)
    list_per_page = 20
    list_display_links = ('email',)
    list_editable = ('is_active', 'is_staff', 'is_superuser')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'subscription_status', 'listing_generation_quota', 'api_call_quota')
    search_fields = ('user__email',)
    list_filter = ('plan', 'subscription_status')
    ordering = ('user__email',)
    list_per_page = 20
    list_display_links = ('user',)
    list_editable = ('plan', 'subscription_status')