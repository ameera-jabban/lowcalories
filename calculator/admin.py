from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import CalorieCalculation


@admin.register(CalorieCalculation)
class CalorieCalculationAdmin(ModelAdmin):
    """هون تشوف كل شخص حسب سعراته — مصدر Leads ممتاز للمتابعة والتسويق"""
    list_display = ("created_at", "gender", "age", "goal", "result_calories", "suggested_plan", "customer_phone")
    list_filter = ("goal", "gender", "activity_level")
    search_fields = ("customer_phone", "progress_code")
    readonly_fields = [f.name for f in CalorieCalculation._meta.fields]

    def has_add_permission(self, request):
        return False  # هذي بتتعبى بس من الموقع، مو يدوياً
