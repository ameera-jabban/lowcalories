from django import forms
from django.utils.translation import gettext_lazy as _

from .models import CalorieCalculation


class CalorieForm(forms.Form):
    gender = forms.ChoiceField(choices=CalorieCalculation.GENDER_CHOICES, label=_("الجنس"))
    age = forms.IntegerField(min_value=12, max_value=90, label=_("العمر"))
    height_cm = forms.IntegerField(min_value=100, max_value=250, label=_("الطول (سم)"))
    weight_kg = forms.IntegerField(min_value=30, max_value=300, label=_("الوزن (كغ)"))
    activity_level = forms.ChoiceField(
        choices=CalorieCalculation.ACTIVITY_CHOICES, label=_("مستوى النشاط")
    )
    goal = forms.ChoiceField(choices=CalorieCalculation.GOAL_CHOICES, label=_("هدفك"))
    customer_phone = forms.CharField(
        required=False, max_length=20,
        label=_("رقم هاتفك (اختياري) — احفظ نتيجتك لتقارنها المرة الجاية"),
        widget=forms.TextInput(attrs={"inputmode": "tel", "placeholder": "962795551234"}),
    )

    def clean_customer_phone(self):
        return self.cleaned_data.get("customer_phone", "").strip().replace(" ", "").lstrip("+")


class ProgressLookupForm(forms.Form):
    phone = forms.CharField(
        label=_("رقم الهاتف"), max_length=20,
        widget=forms.TextInput(attrs={"inputmode": "tel"}),
    )
    progress_code = forms.CharField(label=_("كود المتابعة"), max_length=8)

    def clean_phone(self):
        return self.cleaned_data["phone"].strip().replace(" ", "").lstrip("+")

    def clean_progress_code(self):
        return self.cleaned_data["progress_code"].strip().upper()
