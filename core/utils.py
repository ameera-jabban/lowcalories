"""
أداة مركزية لاختيار النص الصحيح (عربي/إنجليزي) حسب لغة الصفحة الحالية.
تُستخدم بكل الموديلات اللي فيها حقول name_ar/name_en أو content_ar/content_en.
"""
from django.utils.translation import get_language


def localized_field(obj, field_base: str) -> str:
    """
    يرجّع obj.<field_base>_en إذا اللغة الحالية إنجليزي وفيه قيمة،
    وإلا يرجع obj.<field_base>_ar (fallback آمن لو الترجمة الإنجليزية
    لسه ما انضافت لهاي القطعة من المحتوى تحديداً).
    """
    if get_language() == "en":
        en_value = getattr(obj, f"{field_base}_en", "")
        if en_value:
            return en_value
    return getattr(obj, f"{field_base}_ar")


def whatsapp_redirect_url(message="", fallback_url_name="plans:plans_list"):
    """
    رابط واتساب للـ redirect من الـ views. لو ما في رقم واتساب صالح بالإعدادات
    نرجّع رابط صفحة بديلة (الخطط افتراضياً) بدل رابط wa.me مكسور.
    مصدر الرقم الوحيد = SiteSettings.
    """
    from django.urls import reverse

    from core.models import SiteSettings

    return SiteSettings.get_solo().whatsapp_link(message) or reverse(fallback_url_name)
