from django.shortcuts import redirect, render

from menu.models import WeeklyMenu
from .forms import CalorieForm, ProgressLookupForm
from .models import CalorieCalculation
from .services import calculate_result, suggest_plan


def calorie_calculator(request):
    """
    GET: يعرض الفورم فاضي.
    POST: يحسب فعلياً على السيرفر، يخزن النتيجة بقاعدة البيانات (Lead تحليلي)،
          ويقترح خطة اشتراك مناسبة + يعرض المنيو الأسبوعي الحالي تحتها (نفس تجربة mightygainz).
    """
    result = None
    suggested = None
    progress_code = ""
    form = CalorieForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        result = calculate_result(
            gender=data["gender"],
            weight_kg=data["weight_kg"],
            height_cm=data["height_cm"],
            age=data["age"],
            activity_level=data["activity_level"],
            goal=data["goal"],
        )
        suggested = suggest_plan(result["calories"], data["goal"])

        # كود المتابعة يُنشأ فقط لو انعبّى رقم الهاتف (نفس الكود لو الرقم استُخدم قبل)
        phone = data.get("customer_phone", "")
        if phone:
            progress_code = CalorieCalculation.code_for_phone(phone)

        # نخزن النتيجة — تفيدنا لاحقاً بمعرفة أكتر الأهداف طلباً، ومتابعة اللي حسبوا بس ما اشتركوا
        CalorieCalculation.objects.create(
            gender=data["gender"],
            age=data["age"],
            height_cm=data["height_cm"],
            weight_kg=data["weight_kg"],
            activity_level=data["activity_level"],
            goal=data["goal"],
            result_calories=result["calories"],
            result_protein_g=result["protein_g"],
            result_carbs_g=result["carbs_g"],
            result_fat_g=result["fat_g"],
            suggested_plan=suggested,
            customer_phone=phone,
            progress_code=progress_code if phone else "",
        )

    # upsell استشارة التغذية — يظهر مع أي نتيجة (الاستشارة صارت "طلب" بسيط، بدون مواعيد)
    show_consultation_upsell = bool(result)

    # الخطة المقترحة كبطاقة .mcard الموحّدة
    suggested_card = None
    if suggested:
        from django.urls import reverse
        from django.utils.translation import gettext as _
        from core.homepage import _card_image
        suggested_card = {
            "variant": "plan", "layout": "overlay",
            "href": reverse("leads:go_to_whatsapp", args=[suggested.id]) + "?source=calculator",
            "external": True,
            "image": _card_image(getattr(suggested.meal_type, "image", None)),
            "image_alt": suggested.meal_type.name,
            "title": suggested.meal_type.name,
            "macros": [{"key": k, "pct": v} for k, v in suggested.meal_type.macro_split],
            "meta": [
                _("%(d)s يوم") % {"d": suggested.days},
                _("%(m)s وجبة/يوم") % {"m": suggested.meals_per_day},
            ],
            "price_label": _("تبدأ من"),
            "price": suggested.price_jod,
            "currency": _("د.أ"),
        }

    context = {
        "form": form,
        "result": result,
        "suggested_plan": suggested,
        "suggested_card": suggested_card,
        "current_menu": WeeklyMenu.get_current(),
        "show_consultation_upsell": show_consultation_upsell,
        "progress_code": progress_code,
    }
    return render(request, "calculator/calculator.html", context)


def my_progress(request):
    """
    متابعة التقدّم — محمية بـ (رقم الهاتف + كود المتابعة) معاً.

    ⚠️ خصوصية: لو الرقم موجود بس الكود غلط، نرجّع رسالة عامة "بيانات غير صحيحة"
    بدون ما نكشف إذا الرقم مستخدم قبل أو لأ (تسريب معلومة عن مين استخدم الحاسبة).

    المستخدم المسجّل دخول: «متابعة تقدّمي» صارت تبويب داخل «حسابي» — نحوّله لهناك
    (ما في نسختين من نفس الواجهة). غير المسجّل: يكمل بتحقّق الرقم + كود المتابعة.
    """
    if request.session.get("customer_id"):
        return redirect("accounts:progress")

    form = ProgressLookupForm(request.POST or None)
    calcs = None
    comparison = None
    error = None

    if request.method == "POST":
        if form.is_valid():
            qs = CalorieCalculation.objects.filter(
                customer_phone=form.cleaned_data["phone"],
                progress_code=form.cleaned_data["progress_code"],
            ).order_by("created_at")
            if qs.exists():
                calcs = list(qs)
                if len(calcs) > 1:
                    first, last = calcs[0], calcs[-1]
                    comparison = {
                        "from_date": first.created_at,
                        "to_date": last.created_at,
                        "from_weight": first.weight_kg,
                        "to_weight": last.weight_kg,
                        "delta": last.weight_kg - first.weight_kg,
                    }
            else:
                error = "generic"
        else:
            error = "generic"

    return render(
        request,
        "calculator/my_progress.html",
        {"form": form, "calcs": calcs, "comparison": comparison, "error": error},
    )
