import json
from itertools import groupby

from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_GET

from core.homepage import CARD_FALLBACK_IMAGE
from menu.models import MealType
from .models import DiscountCode, Plan


def _plan_card(plan, *, macro_labels, currency, popular_badge, cta_label):
    """
    dict متوافق مع core/_media_card.html (تخطيط overlay) — نفس بطاقة الصورة-أولاً
    المعتمدة بالصفحة الرئيسية، مع إضافة زر CTA وسعر قابل للخصم لهالصفحة.
    الصورة مؤقتاً موحّدة (ChickenSatayBowl) لأن MealType ما إله صورة فردية بعد.
    """
    mt = plan.meal_type
    if plan.meals_per_day == 1:
        title_sub = _("وجبة واحدة / اليوم")
    else:
        title_sub = _("%(n)s وجبات / اليوم") % {"n": plan.meals_per_day}
    price = f"{plan.price_jod:.2f}"
    order_url = reverse("leads:go_to_whatsapp", args=[plan.id]) + "?source=plans_page"
    return {
        "variant": "plan",
        "layout": "overlay",
        "image": CARD_FALLBACK_IMAGE,
        "image_alt": mt.name,
        "popular": plan.is_popular,
        "badge": popular_badge if plan.is_popular else None,
        "title": mt.name,
        "title_sub": title_sub,
        "macros": [{"key": k, "pct": v} for k, v in mt.macro_split],
        "macro_legend": [
            {"key": k, "label": macro_labels[k], "value": f"{v}%"} for k, v in mt.macro_split
        ],
        "price": price,
        "price_raw": price,
        "currency": currency,
        "cta": {"label": cta_label, "href": order_url, "onclick": "fbqLead()"},
    }


def plans_list(request):
    """
    يجيب كل الخطط من قاعدة البيانات ويجمعها حسب عدد الأيام (20 يوم / 24 يوم / 26 يوم).
    كل خطة تتحوّل لبطاقة .mcard المعتمدة (نفس مكوّن الصفحة الرئيسية) — ما في تصميم بطاقة جديد.
    """
    all_plans = Plan.objects.select_related("meal_type").all()
    card_opts = {
        "macro_labels": {"protein": _("بروتين"), "carbs": _("كارب"), "fat": _("دهون")},
        "currency": _("د.أ"),
        "popular_badge": _("الأكثر طلباً"),
        "cta_label": _("اشترك الآن"),
    }
    grouped = {
        days: [_plan_card(p, **card_opts) for p in items]
        for days, items in groupby(all_plans, key=lambda p: p.days)
    }

    # /plans/ صفحة تحويل مركّزة: قارن → اختر → اشترك. بدون أقسام تسويقية إضافية.
    return render(request, "plans/plans_list.html", {"grouped_plans": grouped})


def builder(request):
    """
    مُكوّن خطة الاشتراك — تجربة موجّهة تشتق كل شي (الأنواع المتاحة، عدد الوجبات،
    المدد، السعر، التوفّر) من موديل Plan نفسه (مصدر حقيقة واحد — ما في مصفوفة
    أسعار مكررة). زر «متابعة» يبني رسالة واتساب عبر نفس مسار leads.go_to_whatsapp.
    """
    plans = list(Plan.objects.select_related("meal_type").all())
    matrix = [
        {
            "id": p.id,
            "type": p.meal_type.slug,
            "typeName": str(p.meal_type.name),
            "meals": p.meals_per_day,
            "days": p.days,
            "price": float(p.price_jod),
            "popular": p.is_popular,
        }
        for p in plans
    ]
    used_types = {m["type"] for m in matrix}
    macro_labels = {"protein": _("بروتين"), "carbs": _("كارب"), "fat": _("دهون")}
    meal_types = [
        {
            "slug": mt.slug,
            "name": str(mt.name),
            "macros": [{"key": k, "pct": v} for k, v in mt.macro_split],
            "macro_legend": [
                {"label": macro_labels[k], "value": f"{v}%"} for k, v in mt.macro_split
            ],
        }
        for mt in MealType.objects.all()
        if mt.slug in used_types
    ]

    content = {
        "title": _("اصنع خطتك المثالية"),
        "intro": _("اختر تفضيلاتك خطوة بخطوة وشوف السعر مباشرة."),
        "step_type": _("اختر نوع الخطة"),
        "step_meals": _("كم وجبة باليوم؟"),
        "step_days": _("اختر مدة الاشتراك"),
        "meal_singular": _("وجبة / اليوم"),
        "meal_plural": _("وجبات / اليوم"),
        "day_word": _("يوم"),
        "view_menu": _("شوف المنيو"),
        "summary_title": _("خطتك"),
        "summary_empty_text": _("اختر تفضيلاتك ويظهر ملخّص خطتك هنا."),
        "label_type": _("النوع"),
        "label_meals": _("الوجبات"),
        "label_days": _("المدة"),
        "total": _("المجموع"),
        "jod": _("د.أ"),
        "continue": _("متابعة عبر واتساب"),
        "unavailable": _("هذه التركيبة غير متاحة حالياً — جرّب خياراً آخر."),
    }

    return render(request, "plans/builder.html", {
        "matrix_json": json.dumps(matrix, ensure_ascii=False),
        "meal_types": meal_types,
        "min_price": min((m["price"] for m in matrix), default=0),
        "c": content,
        "go_url_base": reverse("leads:go_to_whatsapp", args=[0]).rsplit("0/", 1)[0],
        "menu_url": reverse("menu:menu_list"),
    })


@require_GET
def validate_code(request, code):
    """
    نقطة تحقّق خفيفة يناديها JS بصفحة الخطط عند إدخال كود خصم.
    ترجّع نسبة الخصم (والـ JS يحسب السعر المخفّض محلياً) أو رسالة خطأ.
    """
    dc = DiscountCode.objects.filter(code__iexact=code.strip()).first()
    if dc and dc.is_valid():
        return JsonResponse({
            "valid": True,
            "code": dc.code,
            "discount_percent": dc.discount_percent,
        })
    return JsonResponse({"valid": False, "error": _("هذا الكود غير صالح أو منتهي.")}, status=200)
