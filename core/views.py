from django.http import Http404, HttpResponse
from django.shortcuts import render

from plans.models import DeliveryArea, Plan
from .models import FAQ, Policy


def _hero_stat(site_settings):
    """
    سطر ثقة صادق فقط — ما نخترع أرقام. كل النصوص تمرّ بنظام الترجمة (i18n)
    مع تمرير الرقم عبر interpolation — مصدر الرقم الوحيد هو الداتا (DeliveryArea / SiteSettings).
    """
    from django.utils.translation import gettext as _

    if site_settings.hero_stat:  # نص يدوي من لوحة التحكم (localized property)
        return site_settings.hero_stat
    if site_settings.reviews_count:
        return _("★ %(rating)s — %(count)s تقييم") % {
            "rating": site_settings.google_rating,
            "count": site_settings.reviews_count,
        }
    areas = DeliveryArea.objects.filter(is_active=True).count()
    if areas:
        return _("نوصّل لـ %(count)s منطقة داخل عمّان") % {"count": areas}
    return ""


def home(request):
    """
    الصفحة الرئيسية. كل الأقسام (hero، الخطط، المرونة، كيف يعمل، التقييمات، FAQ)
    تُبنى من core.homepage عبر context processor ({{ home.* }}). هون بس سطر الثقة
    وأشهر خطة كـ fallback له.
    """
    from .models import SiteSettings

    site_settings = SiteSettings.get_solo()
    return render(request, "core/home.html", {
        "popular_plan": Plan.objects.filter(is_popular=True).first(),
        "hero_stat": _hero_stat(site_settings),
    })


def faq(request):
    from .homepage import get_faq_section
    return render(request, "core/faq.html", {
        "faqs": FAQ.objects.filter(is_published=True),
        "faq": get_faq_section(request, homepage=False),
    })


def policy_detail(request, slug):
    """
    صفحة سياسة/محتوى قانوني ديناميكية. تُعرض فقط لو السياسة منشورة *و* فيها
    محتوى فعلي — غير هيك 404 (بدون صفحة فاضية). كل بيانات التواصل جوّا الصفحة
    تُقرأ من SiteSettings (مصدر الحقيقة الوحيد).
    """
    policy = Policy.get_by_slug(slug)
    if policy is None or not policy.has_content:
        raise Http404("Policy not found")
    return render(request, "core/policy_page.html", {"policy": policy})


def health_check(request):
    """
    Endpoint بسيط تحتاجه أغلب منصات الاستضافة (Render, Railway, load balancers)
    للتأكد إن السيرفر حي وقادر يوصل لقاعدة البيانات فعلاً — مو بس إنه شغال.
    """
    from django.db import connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return HttpResponse("ok", content_type="text/plain")
    except Exception as e:
        return HttpResponse(f"db error: {e}", status=503, content_type="text/plain")
