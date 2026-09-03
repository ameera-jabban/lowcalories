from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from unfold.admin import ModelAdmin

from .models import DeliveryArea, DiscountCode, Plan


@admin.register(Plan)
class PlanAdmin(SimpleHistoryAdmin, ModelAdmin):
    list_display = ("days", "meal_type", "meals_per_day", "price_jod", "is_popular", "has_image")
    list_select_related = ("meal_type",)
    list_filter = ("days", "meal_type", "is_popular")
    list_editable = ("price_jod", "is_popular")  # تعديل السعر مباشرة من القائمة بدون فتح الصفحة
    fields = ("days", "meal_type", "meals_per_day", "price_jod", "is_popular", "image")

    @admin.display(description="صورة خاصة", boolean=True)
    def has_image(self, obj):
        return bool(obj.image)


@admin.register(DeliveryArea)
class DeliveryAreaAdmin(SimpleHistoryAdmin, ModelAdmin):
    list_display = ("name_ar", "name_en", "is_active")
    list_editable = ("is_active",)
    search_fields = ("name_ar", "name_en")


@admin.register(DiscountCode)
class DiscountCodeAdmin(ModelAdmin):
    list_display = ("code", "discount_percent", "usage", "is_active", "valid_until")
    list_editable = ("is_active",)
    list_filter = ("is_active",)
    search_fields = ("code",)
    readonly_fields = ("used_count",)

    @admin.display(description="الاستخدامات")
    def usage(self, obj):
        return f"{obj.used_count} / {obj.max_uses}" if obj.max_uses else f"{obj.used_count} / ∞"
