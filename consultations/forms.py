from django import forms
from django.utils.translation import gettext_lazy as _

from .models import ConsultationRequest


class ConsultationRequestForm(forms.ModelForm):
    class Meta:
        model = ConsultationRequest
        fields = ["full_name", "phone", "email", "preferred_contact", "goal", "notes"]
        widgets = {
            "phone": forms.TextInput(attrs={
                "inputmode": "tel", "dir": "ltr", "placeholder": "07 9 000 0000",
            }),
            "email": forms.EmailInput(attrs={"dir": "ltr", "placeholder": "name@example.com"}),
            "preferred_contact": forms.RadioSelect,
            "goal": forms.TextInput(attrs={
                "placeholder": _("مثال: خسارة وزن، خطة وجبات، نصائح رياضية…"),
            }),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_phone(self):
        return self.cleaned_data["phone"].strip().replace(" ", "").lstrip("+")

    def clean_full_name(self):
        return self.cleaned_data["full_name"].strip()
