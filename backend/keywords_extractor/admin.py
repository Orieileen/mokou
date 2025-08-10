from django.contrib import admin
from .models import KeywordSeed

# Register your models here.
@admin.register(KeywordSeed)
class KeywordSeedAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "category", "created_at", "updated_at"]
    search_fields = ["name"]
    list_filter = ["category", "created_at", "updated_at", "user"]
    ordering = ["-created_at"]
    list_per_page = 10
    list_display_links = ["id"]
    list_select_related = ["category", "user"]