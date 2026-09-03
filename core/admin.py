from django import forms
from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from unfold.admin import ModelAdmin, StackedInline

from .audit import install_audit_dashboard
from .models import (
    FAQ,
    HeroGoal,
    HowItWorksStep,
    Policy,
    PolicySection,
    SiteFeature,
    SiteSettings,
    Testimonial,
)

admin.site.index_title = "إدارة الموقع"


class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = "__all__"
        widgets = {
            "primary_color": forms.TextInput(attrs={"type": "color"}),
            "secondary_color": forms.TextInput(attrs={"type": "color"}),
            "soft_bg_color": forms.TextInput(attrs={"type": "color"}),
        }


@admin.register(SiteSettings)
class SiteSettingsAdmin(SimpleHistoryAdmin, ModelAdmin):
    """
    singleton — دايماً صف واحد بس، يمنع إضافة أكتر من واحد.

    الصلاحيات: فوق منطق الـ singleton، كل صلاحيات Django القياسية محترمة —
    يعني مستخدم ما عنده `core.*` permissions (أي مستخدم مو "مدير عام") ما
    بيوصل هاي الصفحة إطلاقاً (لا بالـ sidebar ولا بالرابط المباشر → 403).
    """
    form = SiteSettingsForm
    fieldsets = (
        ("الهوية", {"fields": ("brand_name_ar", "brand_name_en", "tagline_ar", "tagline_en", "logo",
                               "hero_image", "hero_image_focus", "hero_video_url")}),
        ("سطر الثقة تحت الـ Hero", {"fields": ("hero_stat_ar", "hero_stat_en")}),
        ("ألوان الهوية البصرية", {"fields": ("primary_color", "secondary_color", "soft_bg_color")}),
        ("استشارة التغذية", {"fields": ("consultation_price_jod", "consultation_duration_min")}),
        ("التواصل (مصدر الحقيقة الوحيد)", {
            "description": "كل عناصر واتساب/إنستغرام/الموقع بالموقع بتقرأ من هون. "
                           "غيّر الرقم هون = بيتغير بكل مكان تلقائياً. اترك أي حقل فاضي = يختفي العنصر بأمان.",
            "fields": ("whatsapp_number", "whatsapp_display",
                       "whatsapp_default_message_ar", "whatsapp_default_message_en",
                       "phone_number", "support_email",
                       "instagram_url", "instagram_username",
                       "location_ar", "location_en",
                       "working_hours_ar", "working_hours_en"),
        }),
        ("روابط قانونية قديمة (اختياري — يُفضّل استخدام صفحات السياسات)", {
            "classes": ("collapse",),
            "fields": ("privacy_policy_url", "terms_url"),
        }),
        ("التطبيق والتقييمات", {
            "fields": ("app_store_url", "google_play_url", "google_rating", "reviews_count", "reviews_embed_code")
        }),
        ("التتبع الإعلاني", {"fields": ("facebook_pixel_id",)}),
    )

    def has_add_permission(self, request):
        # لازم يملك صلاحية الإضافة القياسية *و* ما يكون في صف موجود أصلاً
        return super().has_add_permission(request) and not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False  # singleton — ما ينحذف أبداً


@admin.register(Testimonial)
class TestimonialAdmin(ModelAdmin):
    list_display = ("customer_name", "rating", "is_featured", "order", "is_published", "created_at")
    list_editable = ("is_featured", "order", "is_published")
    list_filter = ("rating", "is_published", "is_featured")


@admin.register(SiteFeature)
class SiteFeatureAdmin(ModelAdmin):
    list_display = ("title_ar", "icon", "order", "is_active")
    list_editable = ("order", "is_active")
    list_filter = ("is_active",)


@admin.register(HeroGoal)
class HeroGoalAdmin(ModelAdmin):
    list_display = ("text_ar", "text_en", "order", "is_active")
    list_editable = ("order", "is_active")


@admin.register(HowItWorksStep)
class HowItWorksStepAdmin(ModelAdmin):
    list_display = ("order", "title_ar", "image", "is_active")
    list_editable = ("is_active",)
    ordering = ("order",)


@admin.register(FAQ)
class FAQAdmin(ModelAdmin):
    list_display = ("question_ar", "category_ar", "order", "show_on_homepage", "is_published")
    list_editable = ("order", "show_on_homepage", "is_published")
    list_filter = ("is_published", "show_on_homepage", "category_ar")


class PolicySectionInline(StackedInline):
    model = PolicySection
    extra = 1
    fields = (
        "order",
        ("heading_ar", "heading_en"),
        ("body_ar", "body_en"),
        "list_type",
        ("list_items_ar", "list_items_en"),
    )


@admin.register(Policy)
class PolicyAdmin(SimpleHistoryAdmin, ModelAdmin):
    """
    صفحات قانونية ديناميكية. ما تنشر سياسة إلا بعد إضافة النص القانوني المعتمد
    بأقسامها — السياسة بدون محتوى ما بتظهر ولا بتفتح صفحة (404).
    """
    list_display = ("title_ar", "slug", "is_published", "show_in_footer", "order", "last_updated")
    list_editable = ("is_published", "show_in_footer", "order")
    list_filter = ("is_published", "show_in_footer")
    prepopulated_fields = {"slug": ("title_en",)}
    inlines = [PolicySectionInline]
    fieldsets = (
        ("العنوان والرابط", {"fields": ("title_ar", "title_en", "slug")}),
        ("النشر", {"fields": ("is_published", "show_in_footer", "order")}),
        ("معلومات النسخة", {"fields": ("version", "last_updated")}),
        ("SEO", {"classes": ("collapse",), "fields": ("meta_description_ar", "meta_description_en")}),
    )


# يضيف رابط /admin/audit/recent-changes/ (صفحة "آخر 20 تعديل عبر الموقع")
install_audit_dashboard(admin.site)
