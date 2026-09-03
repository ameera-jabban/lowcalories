from django import forms
from django.utils.translation import gettext_lazy as _


class CustomerLoginForm(forms.Form):
    phone_number = forms.CharField(
        label=_("رقم الهاتف"),
        max_length=20,
        widget=forms.TextInput(attrs={"inputmode": "tel", "placeholder": "962795551234"}),
    )
    access_code = forms.CharField(
        label=_("كود الدخول"),
        max_length=12,
        widget=forms.TextInput(attrs={"autocomplete": "one-time-code"}),
    )

    def clean_phone_number(self):
        # نوحّد الرقم: نشيل الفراغات وعلامة + وأي صفر بادئ محلي
        raw = self.cleaned_data["phone_number"].strip().replace(" ", "").lstrip("+")
        return raw

    def clean_access_code(self):
        return self.cleaned_data["access_code"].strip().upper()


class ReviewForm(forms.Form):
    RATING_CHOICES = [(i, f"{i} ★") for i in range(5, 0, -1)]

    rating = forms.TypedChoiceField(
        label=_("تقييمك"), choices=RATING_CHOICES, coerce=int, initial=5,
        widget=forms.RadioSelect,
    )
    text = forms.CharField(
        label=_("رأيك بالتجربة"),
        widget=forms.Textarea(attrs={"rows": 4}),
        max_length=1000,
    )
