from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import CorporateInquiry, CorporatePlan


@admin.register(CorporatePlan)
class CorporatePlanAdmin(ModelAdmin):
    list_display = ("employee_range", "meal_type", "price_per_employee_jod")
    list_filter = ("meal_type",)
    search_fields = ("description",)

    @admin.display(description="شريحة الموظفين")
    def employee_range(self, obj):
        return obj.employee_range


@admin.register(CorporateInquiry)
class CorporateInquiryAdmin(ModelAdmin):
    list_display = (
        "company_name", "contact_person", "contact_phone",
        "employee_count", "delivery_location", "created_at",
    )
    list_filter = ("created_at",)
    list_per_page = 50
    search_fields = ("company_name", "contact_person", "contact_phone", "delivery_location")
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"
