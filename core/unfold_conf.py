"""
إعداد django-unfold — نفس فلسفة jazzmin_conf القديم: هوية البراند (الاسم/اللوجو)
تُقرأ ديناميكياً من SiteSettings عند كل طلب عبر callbacks، مو hardcoded.

كل الوصول لقاعدة البيانات محاط بـ try/except عشان `manage.py check` / `migrate`
(قبل وجود الجداول) ما يفشلوا.

المُستهلك: `settings.UNFOLD = build_unfold_settings()`.
"""
from __future__ import annotations

from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


def _asset(path):
    """callable — يُحوّل مسار static وقت الطلب (يحترم hashing الإنتاج)."""
    return lambda request: static(path)

_FALLBACK_BRAND = "Low Calories Jordan"


# --------------------------------------------------------------------------- #
# هوية ديناميكية من SiteSettings
# --------------------------------------------------------------------------- #
def _site():
    try:
        from core.models import SiteSettings

        return SiteSettings.get_solo()
    except Exception:
        return None


def _brand_name(request=None) -> str:
    site = _site()
    if site is not None:
        return site.brand_name_en or site.brand_name_ar or _FALLBACK_BRAND
    return _FALLBACK_BRAND


def site_header(request):
    return _brand_name(request)


def site_title(request):
    return f"{_brand_name(request)} — {_('لوحة التحكم')}"


def site_subheader(request):
    return _("لوحة عمليات Low Calories")


# --------------------------------------------------------------------------- #
# صلاحيات عناصر الشريط الجانبي — يخفي ما لا يملك المستخدم صلاحية رؤيته
# --------------------------------------------------------------------------- #
def _can(*perms):
    def check(request):
        u = getattr(request, "user", None)
        return bool(u and (u.is_superuser or any(u.has_perm(p) for p in perms)))
    return check


def _nav(label, url_name, *perms, icon=""):
    return {
        "title": label,
        "link": reverse_lazy(url_name),
        "icon": icon,
        "permission": _can(*perms) if perms else None,
    }


# --------------------------------------------------------------------------- #
# البناء
# --------------------------------------------------------------------------- #
def build_unfold_settings() -> dict:
    return {
        "SITE_TITLE": site_title,
        "SITE_HEADER": site_header,
        "SITE_SUBHEADER": site_subheader,
        "SITE_URL": "/",
        "SITE_ICON": lambda request: static("img/brand-mark.svg"),
        "SITE_SYMBOL": "restaurant",
        "SITE_FAVICONS": [
            {"rel": "icon", "href": lambda request: static("img/favicon.ico"), "sizes": "32x32"},
            {"rel": "icon", "href": lambda request: static("img/brand-mark.svg"), "type": "image/svg+xml"},
            {"rel": "apple-touch-icon", "href": lambda request: static("img/favicon.png")},
        ],
        "SHOW_HISTORY": True,
        "SHOW_VIEW_ON_SITE": True,
        "SHOW_LANGUAGES": True,          # مبدّل اللغة بالـ shell (core.middleware.AdminLocaleMiddleware)
        "BORDER_RADIUS": "6px",
        # إصلاحات تخطيط RTL + قيم تقنية LTR — بنطاق [dir="rtl"] فقط، ما يمسّ الإنجليزي
        "STYLES": [_asset("admin/css/admin-rtl.css")],
        "DASHBOARD_CALLBACK": "core.admin_dashboard.dashboard_callback",
        # ---- برتقالي البراند كـ accent محكوم (مش خلفية everywhere) ----
        "COLORS": {
            "primary": {
                "50": "#fff4e8",
                "100": "#ffe4c7",
                "200": "#ffc98a",
                "300": "#ffa94d",
                "400": "#fb8b1e",
                "500": "#f0791e",
                "600": "#d0640f",
                "700": "#a85400",
                "800": "#874402",
                "900": "#6f3a06",
                "950": "#3f1e02",
            },
        },
        "SIDEBAR": {
            "show_search": True,
            "show_all_applications": False,
            "navigation": [
                {
                    "title": _("نظرة عامة"),
                    "separator": False,
                    "items": [
                        {"title": _("لوحة القيادة"), "link": reverse_lazy("admin:index"), "icon": "dashboard"},
                        {
                            "title": _("آخر التعديلات"),
                            "link": reverse_lazy("admin:audit_recent_changes"),
                            "icon": "history",
                            "permission": _can("core.change_sitesettings"),
                        },
                    ],
                },
                {
                    "title": _("العملاء والطلبات"),
                    "separator": True,
                    "items": [
                        _nav(_("العملاء"), "admin:accounts_customer_changelist", "accounts.view_customer", icon="group"),
                        _nav(_("طلبات الاستشارات"), "admin:consultations_consultationrequest_changelist", "consultations.view_consultationrequest", icon="support_agent"),
                        _nav(_("طلبات عروض الشركات"), "admin:corporate_corporateinquiry_changelist", "corporate.view_corporateinquiry", icon="corporate_fare"),
                        _nav(_("الإحالات"), "admin:referrals_referral_changelist", "referrals.view_referral", icon="share"),
                        _nav(_("أكواد الإحالة"), "admin:referrals_referralcode_changelist", "referrals.view_referralcode", icon="qr_code_2"),
                    ],
                },
                {
                    "title": _("الاشتراكات والتسعير"),
                    "separator": True,
                    "items": [
                        _nav(_("خطط الاشتراك"), "admin:plans_plan_changelist", "plans.view_plan", icon="inventory_2"),
                        _nav(_("اشتراكات العملاء"), "admin:accounts_subscription_changelist", "accounts.view_subscription", icon="event_repeat"),
                        _nav(_("نوايا الشراء (Leads)"), "admin:leads_lead_changelist", "leads.view_lead", icon="ads_click"),
                        _nav(_("أكواد الخصم"), "admin:plans_discountcode_changelist", "plans.view_discountcode", icon="sell"),
                        _nav(_("خطط الشركات"), "admin:corporate_corporateplan_changelist", "corporate.view_corporateplan", icon="business_center"),
                    ],
                },
                {
                    "title": _("المنيو والتغذية"),
                    "separator": True,
                    "items": [
                        _nav(_("أنواع الوجبات"), "admin:menu_mealtype_changelist", "menu.view_mealtype", icon="restaurant_menu"),
                        _nav(_("المنيو الأسبوعي"), "admin:menu_weeklymenu_changelist", "menu.view_weeklymenu", icon="calendar_month"),
                        _nav(_("الوجبات"), "admin:menu_menuitem_changelist", "menu.view_menuitem", icon="lunch_dining"),
                        _nav(_("نتائج حاسبة السعرات"), "admin:calculator_caloriecalculation_changelist", "calculator.view_caloriecalculation", icon="calculate"),
                    ],
                },
                {
                    "title": _("التوصيل"),
                    "separator": True,
                    "items": [
                        _nav(_("مناطق التوصيل"), "admin:plans_deliveryarea_changelist", "plans.view_deliveryarea", icon="local_shipping"),
                    ],
                },
                {
                    "title": _("المحتوى والإعدادات"),
                    "separator": True,
                    "items": [
                        _nav(_("إعدادات الموقع"), "admin:core_sitesettings_changelist", "core.view_sitesettings", icon="settings"),
                        _nav(_("محتوى الـ Hero"), "admin:core_herogoal_changelist", "core.view_herogoal", icon="wallpaper"),
                        _nav(_("كيف يعمل"), "admin:core_howitworksstep_changelist", "core.view_howitworksstep", icon="format_list_numbered"),
                        _nav(_("الأسئلة الشائعة"), "admin:core_faq_changelist", "core.view_faq", icon="quiz"),
                        _nav(_("تقييمات العملاء"), "admin:core_testimonial_changelist", "core.view_testimonial", icon="reviews"),
                        _nav(_("مزايا الموقع"), "admin:core_sitefeature_changelist", "core.view_sitefeature", icon="star"),
                        _nav(_("السياسات القانونية"), "admin:core_policy_changelist", "core.view_policy", icon="gavel"),
                    ],
                },
                {
                    "title": _("المستخدمون والصلاحيات"),
                    "separator": True,
                    "items": [
                        _nav(_("المستخدمون"), "admin:auth_user_changelist", "auth.view_user", icon="manage_accounts"),
                        _nav(_("الأدوار"), "admin:auth_group_changelist", "auth.view_group", icon="admin_panel_settings"),
                    ],
                },
            ],
        },
    }
