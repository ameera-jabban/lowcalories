from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Referral, ReferralCode


@admin.register(ReferralCode)
class ReferralCodeAdmin(ModelAdmin):
    list_display = ("code", "referrer_name", "referrer_phone", "referrals_count", "redeemed_count", "created_at")
    search_fields = ("code", "referrer_name", "referrer_phone")
    readonly_fields = ("code", "created_at")

    @admin.display(description="عدد الإحالات")
    def referrals_count(self, obj):
        return obj.referrals.count()

    @admin.display(description="مُستبدلة")
    def redeemed_count(self, obj):
        return obj.redeemed_count


@admin.register(Referral)
class ReferralAdmin(ModelAdmin):
    list_display = ("referred_name", "referred_phone", "referrer", "status", "created_at", "redeemed_at")
    list_select_related = ("referral_code",)
    list_editable = ("status",)  # الأدمن يؤكد "صارت اشتراك فعلاً" بضغطة
    list_filter = ("status", "created_at")
    search_fields = ("referred_name", "referred_phone", "referral_code__code", "referral_code__referrer_name")
    readonly_fields = ("created_at", "redeemed_at")
    actions = ["mark_redeemed_and_log"]

    @admin.display(description="صاحب الكود")
    def referrer(self, obj):
        return obj.referral_code.referrer_name

    @admin.action(description="تعليم كمُستبدلة + تسجيل اليوم المجاني")
    def mark_redeemed_and_log(self, request, queryset):
        for referral in queryset:
            note = referral.mark_redeemed()
            self.message_user(request, f"{referral}: {note}")
