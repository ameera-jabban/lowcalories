"""
Audit Log — تجميع نشاط django-simple-history عبر كل الموديلات المتتبَّعة
في صفحة واحدة: "آخر 20 تعديل عبر الموقع".

مفيدة للمدير العام يشوف نشاط الفريق بسرعة بدون ما يفتح تبويب History لكل
موديل لحاله.
"""
from __future__ import annotations

_ACTION_LABELS = {
    "+": ("أُضيف", "success"),
    "~": ("عُدّل", "warning"),
    "-": ("حُذف", "danger"),
}


def _tracked_history_managers():
    """يرجّع (model, history_manager) لكل موديل عليه HistoricalRecords."""
    from django.apps import apps

    for model in apps.get_models():
        manager = getattr(model, "history", None)
        # HistoryManager عنده .model (الموديل الـ Historical) و .most_recent
        if manager is not None and hasattr(manager, "model") and hasattr(manager, "most_recent"):
            yield model, manager


def recent_history_entries(limit: int = 20):
    """قائمة موحّدة ومرتّبة (الأحدث أولاً) من سجلات history عبر كل الموديلات."""
    records = []
    for model, manager in _tracked_history_managers():
        qs = manager.all().select_related("history_user").order_by("-history_date")[:limit]
        for h in qs:
            action_label, action_css = _ACTION_LABELS.get(h.history_type, (h.history_type, "secondary"))
            changed_fields = []
            if h.history_type == "~":
                try:
                    prev = h.prev_record
                    if prev is not None:
                        changed_fields = [
                            model._meta.get_field(c.field).verbose_name
                            for c in h.diff_against(prev).changes
                        ]
                except Exception:
                    changed_fields = []
            records.append(
                {
                    "model_label": model._meta.verbose_name,
                    "object_repr": str(h),
                    "user": h.history_user,
                    "date": h.history_date,
                    "action_label": action_label,
                    "action_css": action_css,
                    "changed_fields": changed_fields,
                }
            )
    records.sort(key=lambda r: r["date"], reverse=True)
    return records[:limit]


def install_audit_dashboard(site):
    """
    يضيف مسار `/admin/audit/recent-changes/` للـ AdminSite الافتراضي بدون
    ما نعمل AdminSite class جديد (يحافظ على بساطة الإعداد الحالي).
    """
    from django.core.exceptions import PermissionDenied
    from django.template.response import TemplateResponse
    from django.urls import path

    _orig_get_urls = site.get_urls

    def recent_changes_view(request):
        # صفحة إدارية حساسة — للمدير العام فقط (اللي يملك صلاحية تعديل الإعدادات)
        if not request.user.has_perm("core.change_sitesettings"):
            raise PermissionDenied

        context = {
            **site.each_context(request),
            "title": "آخر 20 تعديل عبر الموقع",
            "entries": recent_history_entries(20),
        }
        return TemplateResponse(request, "admin/dashboard/recent_changes.html", context)

    def get_urls():
        custom = [
            path(
                "audit/recent-changes/",
                site.admin_view(recent_changes_view),
                name="audit_recent_changes",
            ),
        ]
        return custom + _orig_get_urls()

    site.get_urls = get_urls
