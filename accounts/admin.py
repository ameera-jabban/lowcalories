from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import Customer, Subscription


class SubscriptionInline(TabularInline):
    model = Subscription
    extra = 0
    fields = ("plan", "status", "start_date", "end_date", "frozen_at")
    readonly_fields = ("frozen_at",)


@admin.register(Customer)
class CustomerAdmin(ModelAdmin):
    list_display = ("name", "phone_number", "access_code", "subscriptions_count", "created_at")
    search_fields = ("name", "phone_number", "access_code")
    readonly_fields = ("access_code", "created_at")
    inlines = [SubscriptionInline]

    @admin.display(description="عدد الاشتراكات")
    def subscriptions_count(self, obj):
        return obj.subscriptions.count()


@admin.register(Subscription)
class SubscriptionAdmin(ModelAdmin):
    list_display = (
        "customer", "plan", "status", "start_date", "end_date",
        "days_remaining", "review_requested_at",
    )
    list_select_related = ("customer", "plan", "plan__meal_type")
    list_filter = ("status", "plan__meal_type", "start_date")
    list_editable = ("status",)
    search_fields = ("customer__name", "customer__phone_number")
    autocomplete_fields = ("customer",)
    readonly_fields = ("frozen_at", "review_requested_at", "created_at")
    date_hierarchy = "start_date"

    @admin.display(description="أيام متبقية")
    def days_remaining(self, obj):
        return obj.days_remaining
