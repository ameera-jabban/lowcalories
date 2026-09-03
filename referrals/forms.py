from django import forms
from django.utils.translation import gettext_lazy as _


def _norm_phone(v: str) -> str:
    return v.strip().replace(" ", "").lstrip("+")


class GetCodeForm(forms.Form):
    referrer_name = forms.CharField(label=_("اسمك"), max_length=120)
    referrer_phone = forms.CharField(
        label=_("رقم هاتفك"), max_length=20,
        widget=forms.TextInput(attrs={"inputmode": "tel", "placeholder": "962795551234"}),
    )

    def clean_referrer_phone(self):
        return _norm_phone(self.cleaned_data["referrer_phone"])


class ClaimReferralForm(forms.Form):
    referred_name = forms.CharField(label=_("اسمك"), max_length=120)
    referred_phone = forms.CharField(
        label=_("رقم هاتفك"), max_length=20,
        widget=forms.TextInput(attrs={"inputmode": "tel", "placeholder": "962795551234"}),
    )

    def clean_referred_phone(self):
        return _norm_phone(self.cleaned_data["referred_phone"])
