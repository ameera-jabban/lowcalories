from django.contrib import admin
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin

from .models import ConsultationRequest


@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(ModelAdmin):
    list_display = (
        "reference", "full_name", "phone", "preferred_contact",
        "goal", "status", "created_at",
    )
    list_display_links = ("reference", "full_name")
    list_editable = ("status",)
    list_filter = ("status", "preferred_contact", "source", "created_at")
    search_fields = ("full_name", "phone", "email", "goal", "notes")
    readonly_fields = ("created_at", "language", "source", "contact_links")
    date_hierarchy = "created_at"
    fieldsets = (
        (_("بيانات العميل"), {
            "fields": ("full_name", "phone", "email", "preferred_contact", "contact_links"),
        }),
        (_("الطلب"), {"fields": ("goal", "notes", "source", "language", "created_at")}),
        (_("متابعة الفريق"), {"fields": ("status", "admin_notes")}),
    )

    @admin.display(description=_("المرجع"))
    def reference(self, obj):
        return obj.reference

    @admin.display(description=_("تواصل مع العميل"))
    def contact_links(self, obj):
        links = []
        if obj.whatsapp_url:
            links.append((obj.whatsapp_url, _("تواصل عبر واتساب")))
        if obj.phone:
            links.append(("tel:" + obj.phone, _("اتصال هاتفي")))
        if obj.email:
            links.append(("mailto:" + obj.email, _("بريد إلكتروني")))
        if not links:
            return "—"
        return format_html_join(
            mark_safe(" &nbsp;&middot;&nbsp; "),
            '<a href="{}" target="_blank" rel="noopener">{}</a>',
            links,
        )
