from django.contrib import admin

from .models import Listing


# Register your models here.
@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "category", "status", "pattern_image", "keyword_seed", "created_at", "updated_at", "user"]
    search_fields = ["title", "keyword_seed"]
    list_filter = ["category", "status", "created_at", "updated_at", "user"]
    ordering = ["-created_at"]
    list_per_page = 10
    list_display_links = ["id"]
    list_select_related = ["category", "user"]