"""
حسابي — مركز العميل الموحّد (نظرة عامة، اشتراكات، تقدّمي، بياناتي، إحالة).

الفلسفة (نفس باقي الموقع): ما في سلة/دفع إلكتروني. كل زر "يقترح" إجراء ويجهّز
رسالة واتساب جاهزة — التأكيد النهائي يتم يدوياً من لوحة التحكم. تجميد/استئناف
الاشتراك يحدّثان السجل محلياً، بس التنفيذ الفعلي يؤكده الأدمن.
"""
from __future__ import annotations

from datetime import date

from django.contrib import messages
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _, gettext_lazy
from django.views.decorators.http import require_POST

from core.models import Testimonial
from menu.models import MealType
from .forms import CustomerLoginForm, ReviewForm
from .models import Customer, Subscription

SESSION_KEY = "customer_id"

# تبويبات "حسابي" — (المفتاح، التسمية، اسم المسار). مصدر واحد.
PROFILE_TABS = [
    ("overview", gettext_lazy("نظرة عامة"), "accounts:dashboard"),
    ("subscriptions", gettext_lazy("الاشتراكات"), "accounts:subscriptions"),
    ("progress", gettext_lazy("متابعة تقدّمي"), "accounts:progress"),
    ("personal", gettext_lazy("بياناتي"), "accounts:personal"),
    ("referral", gettext_lazy("الإحالة والمكافآت"), "referrals:get_code"),
]


def _current_customer(request):
    customer_id = request.session.get(SESSION_KEY)
    if not customer_id:
        return None
    return Customer.objects.filter(pk=customer_id).first()


def _profile_ctx(customer, active_tab, extra=None):
    ctx = {"customer": customer, "profile_tabs": PROFILE_TABS, "active_tab": active_tab}
    if extra:
        ctx.update(extra)
    return ctx


def _customer_subscriptions(customer):
    return list(
        customer.subscriptions.select_related("plan", "plan__meal_type").all()
    )


def _sub_progress(sub):
    """(مكتمل، إجمالي، متبقّي، نسبة%) — فقط لو في تواريخ صالحة."""
    if not (sub.start_date and sub.end_date and sub.end_date > sub.start_date):
        return None
    total = (sub.end_date - sub.start_date).days
    done = max(0, min(total, (date.today() - sub.start_date).days))
    return {
        "done": done, "total": total,
        "remaining": max(0, total - done),
        "pct": round(done / total * 100) if total else 0,
    }


def _whatsapp_redirect(message: str):
    from core.utils import whatsapp_redirect_url
    return redirect(whatsapp_redirect_url(message))


def _sub_for_action(request, customer):
    """الاشتراك اللي ينطبق عليه الإجراء: من POST['subscription'] لو تبع العميل، وإلا الفعّال."""
    sid = request.POST.get("subscription")
    if sid:
        return customer.subscriptions.filter(pk=sid).first()
    return customer.active_subscription


# ============================ auth ============================
def login_view(request):
    if _current_customer(request):
        return redirect("accounts:dashboard")

    form = CustomerLoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        customer = Customer.objects.filter(
            phone_number=form.cleaned_data["phone_number"],
            access_code=form.cleaned_data["access_code"],
        ).first()
        if customer:
            request.session[SESSION_KEY] = customer.pk
            return redirect("accounts:dashboard")
        messages.error(request, _("رقم الهاتف أو كود الدخول غير صحيح."))

    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    request.session.pop(SESSION_KEY, None)
    return redirect("accounts:login")


# ============================ profile tabs ============================
def dashboard(request):
    """نظرة عامة — ملخّص مختصر."""
    customer = _current_customer(request)
    if not customer:
        return redirect("accounts:login")

    subs = _customer_subscriptions(customer)
    active = [s for s in subs if s.is_active]
    next_end = min(
        (s.end_date for s in active if s.end_date), default=None
    )
    total_remaining = sum(s.days_remaining for s in active)
    current_plan = active[0].plan.meal_type.name if active else None

    return render(request, "accounts/overview.html", _profile_ctx(customer, "overview", {
        "subscriptions": subs,
        "active_count": len(active),
        "total_remaining": total_remaining,
        "next_end": next_end,
        "current_plan": current_plan,
    }))


def subscriptions_view(request):
    customer = _current_customer(request)
    if not customer:
        return redirect("accounts:login")

    subs = _customer_subscriptions(customer)
    rows = []
    for s in subs:
        rows.append({
            "sub": s,
            "progress": _sub_progress(s),
            "other_meal_types": MealType.objects.exclude(pk=s.plan.meal_type_id),
        })
    return render(request, "accounts/subscriptions.html", _profile_ctx(customer, "subscriptions", {
        "rows": rows,
    }))


def personal_view(request):
    customer = _current_customer(request)
    if not customer:
        return redirect("accounts:login")
    return render(request, "accounts/personal.html", _profile_ctx(customer, "personal"))


def progress_view(request):
    """تقدّم العميل — يُقرأ آلياً من سجل حساباته (بدون كود، لأنه مسجّل دخول)."""
    customer = _current_customer(request)
    if not customer:
        return redirect("accounts:login")

    from calculator.models import CalorieCalculation

    calcs = list(
        CalorieCalculation.objects.filter(customer_phone=customer.phone_number).order_by("created_at")
    )
    comparison = None
    if len(calcs) > 1:
        first, last = calcs[0], calcs[-1]
        comparison = {
            "from_date": first.created_at, "to_date": last.created_at,
            "from_weight": first.weight_kg, "to_weight": last.weight_kg,
            "delta": last.weight_kg - first.weight_kg,
        }
    return render(request, "accounts/progress.html", _profile_ctx(customer, "progress", {
        "calcs": calcs, "comparison": comparison,
    }))


# ============================ subscription actions ============================
@require_POST
def freeze_subscription(request):
    customer = _current_customer(request)
    if not customer:
        return redirect("accounts:login")

    subscription = _sub_for_action(request, customer)
    if not subscription or not subscription.is_active:
        messages.error(request, _("ما في اشتراك فعّال يمكن تجميده."))
        return redirect("accounts:subscriptions")

    subscription.freeze()
    return _whatsapp_redirect(_(
        "مرحبا، أنا %(name)s. أرغب بتجميد اشتراكي (%(plan)s) اعتباراً من اليوم."
    ) % {"name": customer.name, "plan": str(subscription.plan)})


@require_POST
def resume_subscription(request):
    customer = _current_customer(request)
    if not customer:
        return redirect("accounts:login")

    subscription = _sub_for_action(request, customer)
    if not subscription or not subscription.is_frozen:
        messages.error(request, _("ما في اشتراك مجمّد يمكن استئنافه."))
        return redirect("accounts:subscriptions")

    subscription.resume()
    return _whatsapp_redirect(_(
        "مرحبا، أنا %(name)s. أرغب باستئناف اشتراكي (%(plan)s). "
        "تاريخ الانتهاء الجديد بعد التمديد: %(end)s."
    ) % {"name": customer.name, "plan": str(subscription.plan), "end": subscription.end_date})


@require_POST
def swap_meal_type(request):
    customer = _current_customer(request)
    if not customer:
        return redirect("accounts:login")

    subscription = _sub_for_action(request, customer)
    if not subscription:
        messages.error(request, _("ما في اشتراك حالي لتغيير نوع وجباته."))
        return redirect("accounts:subscriptions")

    new_meal_type = get_object_or_404(MealType, pk=request.POST.get("meal_type"))
    return _whatsapp_redirect(_(
        "مرحبا، أنا %(name)s. أرغب بتغيير نوع وجبات اشتراكي من %(old)s إلى %(new)s."
    ) % {"name": customer.name, "old": subscription.plan.meal_type.name, "new": new_meal_type.name})


# ============================ review (from WhatsApp link) ============================
def leave_review(request, access_code):
    customer = Customer.objects.filter(access_code=access_code).first()
    if not customer:
        raise Http404

    form = ReviewForm(request.POST or None)
    submitted = False
    if request.method == "POST" and form.is_valid():
        Testimonial.objects.create(
            customer_name=customer.name,
            rating=form.cleaned_data["rating"],
            text_ar=form.cleaned_data["text"],
            is_published=False,
        )
        submitted = True

    return render(request, "accounts/leave_review.html", {
        "form": form, "customer": customer, "submitted": submitted,
    })
