from django.contrib import admin

from .models import RawListing


# Register your models here.
@admin.register(RawListing)
class RawListingAdmin(admin.ModelAdmin):
    list_display = ["id", "asin", "category", "source", "created_at", "updated_at", "user"]
    search_fields = ["asin"]
    list_filter = ["category", "created_at", "updated_at", "user"]
    ordering = ["-created_at"]
    list_per_page = 10
    list_display_links = ["id"]
    list_select_related = ["category", "user"]