from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from unfold.admin import ModelAdmin, TabularInline

from .models import MealType, WeeklyMenu, MenuItem


@admin.register(MealType)
class MealTypeAdmin(ModelAdmin):
    list_display = ("name_ar", "name_en", "slug", "icon_emoji", "macros")
    prepopulated_fields = {"slug": ("name_en",)}
    fields = ("name_ar", "name_en", "slug", "icon_emoji",
              "typical_protein_pct", "typical_carbs_pct", "typical_fat_pct")

    @admin.display(description="ماكروز %")
    def macros(self, obj):
        return f"{obj.typical_protein_pct}/{obj.typical_carbs_pct}/{obj.typical_fat_pct}"


class MenuItemInline(TabularInline):
    model = MenuItem
    extra = 7  # يوم بكل صف تقريباً
    fields = ("day_of_week", "meal_type", "name_ar", "calories", "protein_g", "carbs_g", "fat_g", "image")


@admin.register(WeeklyMenu)
class WeeklyMenuAdmin(SimpleHistoryAdmin, ModelAdmin):
    list_display = ("week_start_date", "is_active", "items_count")
    list_filter = ("is_active",)
    inlines = [MenuItemInline]

    @admin.display(description="عدد الوجبات")
    def items_count(self, obj):
        return obj.items.count()


@admin.register(MenuItem)
class MenuItemAdmin(SimpleHistoryAdmin, ModelAdmin):
    list_display = ("name_ar", "weekly_menu", "day_of_week", "meal_type", "calories")
    list_select_related = ("weekly_menu", "meal_type")
    list_filter = ("weekly_menu", "meal_type", "day_of_week")
    search_fields = ("name_ar", "name_en")
