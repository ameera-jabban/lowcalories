"""
برنامج الإحالة — نفس فلسفة الموقع: كل شي بينتهي برسالة واتساب جاهزة،
والأدمن يؤكد ويطبّق المكافأة يدوياً (أو تلقائياً عبر أكشن إداري لو accounts موجود).
"""
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from core.models import SiteSettings
from .forms import ClaimReferralForm, GetCodeForm
from .models import Referral, ReferralCode


def get_code(request):
    code_obj = None
    form = GetCodeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        phone = form.cleaned_data["referrer_phone"]
        # لو هالرقم عمل كود قبل، رجّعله نفسه بدل ما ننشئ جديد
        code_obj, _created = ReferralCode.objects.get_or_create(
            referrer_phone=phone,
            defaults={"referrer_name": form.cleaned_data["referrer_name"]},
        )

    share_url = None
    whatsapp_url = None
    if code_obj:
        share_url = request.build_absolute_uri(code_obj.share_path())
        msg = _(
            "بدعوتك تجرّب Low Calories Jordan! اشترك لأول مرة عبر رابطي "
            "وناخد الاثنين يوم مجاني:\n%(url)s"
        ) % {"url": share_url}
        whatsapp_url = SiteSettings.get_solo().whatsapp_link(msg)

    return render(
        request,
        "referrals/get_code.html",
        {"form": form, "code_obj": code_obj, "share_url": share_url, "whatsapp_url": whatsapp_url},
    )


def claim(request, code):
    referral_code = ReferralCode.objects.filter(code=code).first()
    if not referral_code:
        return render(request, "referrals/invalid.html", status=404)

    form = ClaimReferralForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        Referral.objects.create(
            referral_code=referral_code,
            referred_name=form.cleaned_data["referred_name"],
            referred_phone=form.cleaned_data["referred_phone"],
        )
        msg = _(
            "مرحبا! صديقي %(referrer)s دعاني لـ Low Calories Jordan (كود الإحالة: "
            "%(code)s). بدي أشترك لأول مرة."
        ) % {"referrer": referral_code.referrer_name, "code": referral_code.code}
        from core.utils import whatsapp_redirect_url
        return redirect(whatsapp_redirect_url(msg))

    return render(
        request,
        "referrals/claim.html",
        {"form": form, "referral_code": referral_code},
    )
