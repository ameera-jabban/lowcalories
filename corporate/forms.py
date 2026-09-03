from django import forms
from django.utils.translation import gettext_lazy as _

from .models import CorporateInquiry


class CorporateInquiryForm(forms.ModelForm):
    class Meta:
        model = CorporateInquiry
        fields = [
            "company_name", "contact_person", "contact_phone",
            "employee_count", "delivery_location", "notes",
        ]
        labels = {
            "company_name": _("اسم الشركة"),
            "contact_person": _("الشخص المسؤول"),
            "contact_phone": _("رقم التواصل"),
            "employee_count": _("عدد الموظفين التقريبي"),
            "delivery_location": _("موقع التوصيل"),
            "notes": _("ملاحظات (اختياري)"),
        }
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
            "contact_phone": forms.TextInput(attrs={"inputmode": "tel"}),
        }

    def clean_contact_phone(self):
        return self.cleaned_data["contact_phone"].strip().replace(" ", "").lstrip("+")
