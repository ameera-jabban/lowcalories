from django.db.models import F
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext as _

from core.utils import whatsapp_redirect_url
from plans.models import DiscountCode, Plan
from .models import Lead


def go_to_whatsapp(request, plan_id):
    """
    هاد الرابط يوديله كل زر '🍗 دجاج - وجبة 89 د.أ' بصفحة الخطط.
    1) يسجل Lead بقاعدة البيانات (نية شراء حقيقية نقدر نحللها لاحقاً)
    2) لو في كود خصم صالح (?code=): يربطه بالـ Lead، يزيد used_count، ويضيف
       السعر المخفّض للرسالة — ⚠️ استرشادي فقط، الخصم النهائي يطبّقه الأدمن
       يدوياً بمحادثة واتساب (ما في دفع أونلاين).
    3) يحوّل المستخدم فوراً لواتساب برسالة جاهزة فيها تفاصيل الخطة
    """
    plan = get_object_or_404(Plan, pk=plan_id)
    source = request.GET.get("source", "plans_page")

    message = plan.whatsapp_message()
    discount_code = None
    raw_code = (request.GET.get("code") or "").strip()
    if raw_code:
        dc = DiscountCode.objects.filter(code__iexact=raw_code).first()
        if dc and dc.is_valid():
            discount_code = dc
            new_price = dc.discounted_price(plan.price_jod)
            message += "\n" + _(
                "كود خصم: %(code)s (-%(pct)s%%) — السعر بعد الخصم تقريباً %(new)s د بدل %(old)s د"
            ) % {
                "code": dc.code, "pct": dc.discount_percent,
                "new": new_price, "old": plan.price_jod,
            }
            DiscountCode.objects.filter(pk=dc.pk).update(used_count=F("used_count") + 1)

    Lead.objects.create(plan=plan, source_page=source, discount_code=discount_code)

    return redirect(whatsapp_redirect_url(message))


def go_to_whatsapp_general(request):
    """لأزرار واتساب العامة اللي مو مرتبطة بخطة معينة (مثلاً هيرو الصفحة الرئيسية)"""
    source = request.GET.get("source", "general")
    message = request.GET.get("message") or _("مرحبا، بدي أسأل عن Low Calories Jordan")

    Lead.objects.create(plan=None, source_page=source)

    return redirect(whatsapp_redirect_url(message))
