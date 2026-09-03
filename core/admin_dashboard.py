"""
لوحة قيادة الأدمن (Unfold DASHBOARD_CALLBACK).

تجاوب على سؤال واحد: "شو يحتاج انتباه اليوم؟" — أرقام تشغيلية حقيقية فقط،
بدون رسوم زخرفية. تحترم صلاحيات المستخدم: ما يشوف رقم موديل ما يملك صلاحية عرضه.
"""
from __future__ import annotations

from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .audit import recent_history_entries


def _perm(request, codename: str) -> bool:
    u = request.user
    return bool(u.is_superuser or u.has_perm(codename))


def dashboard_callback(request, context):
    today = timezone.localdate()
    week_ago = today - timedelta(days=7)

    from accounts.models import Subscription
    from calculator.models import CalorieCalculation
    from consultations.models import ConsultationRequest
    from corporate.models import CorporateInquiry
    from leads.models import Lead
    from referrals.models import Referral

    cards = []

    def add(label, value, url_name, perm, *, hint=""):
        if _perm(request, perm):
            cards.append({
                "title": label, "value": value, "hint": hint,
                "url": reverse(url_name),
            })

    add(_("طلبات استشارة جديدة"),
        ConsultationRequest.objects.filter(status="new").count(),
        "admin:consultations_consultationrequest_changelist", "consultations.view_consultationrequest",
        hint=_("بانتظار تواصل الفريق"))
    add(_("طلبات عروض شركات جديدة"),
        CorporateInquiry.objects.filter(created_at__date__gte=week_ago).count(),
        "admin:corporate_corporateinquiry_changelist", "corporate.view_corporateinquiry",
        hint=_("آخر 7 أيام"))
    add(_("اشتراكات فعّالة"),
        Subscription.objects.filter(status="active").count(),
        "admin:accounts_subscription_changelist", "accounts.view_subscription")
    add(_("إحالات بانتظار التأكيد"),
        Referral.objects.filter(status="pending").count(),
        "admin:referrals_referral_changelist", "referrals.view_referral")
    add(_("نوايا شراء اليوم"),
        Lead.objects.filter(created_at__date=today).count(),
        "admin:leads_lead_changelist", "leads.view_lead",
        hint=_("إجمالي %(n)s") % {"n": Lead.objects.count()})
    add(_("استخدامات حاسبة السعرات"),
        CalorieCalculation.objects.count(),
        "admin:calculator_caloriecalculation_changelist", "calculator.view_caloriecalculation")

    # نوايا الشراء آخر 7 أيام — رسم CSS بسيط (بدون مكتبات)
    leads_7d = []
    if _perm(request, "leads.view_lead"):
        days = [today - timedelta(days=i) for i in range(6, -1, -1)]
        leads_7d = [
            {"label": d.strftime("%d/%m"), "count": Lead.objects.filter(created_at__date=d).count()}
            for d in days
        ]

    context.update({
        "lc_cards": cards,
        "lc_leads_7d": leads_7d,
        "lc_leads_7d_max": max([r["count"] for r in leads_7d] + [1]),
        "lc_recent": recent_history_entries(8) if _perm(request, "core.change_sitesettings") else [],
        "lc_show_audit_link": _perm(request, "core.change_sitesettings"),
    })
    return context
