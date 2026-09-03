from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Lead


@admin.register(Lead)
class LeadAdmin(ModelAdmin):
    list_display = ("created_at", "plan", "source_page", "discount_code")
    list_select_related = ("plan", "plan__meal_type", "discount_code")
    list_filter = ("source_page", "plan", "discount_code")
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False
