"""
خطط الشركات (B2B): شركة بدها توصيل يومي لموظفيها لموقع واحد.

نفس فلسفة الموقع: `CorporateInquiry` هو نظير B2B لـ `leads.Lead` — الفورم
يخزّن الطلب ثم يحوّل لواتساب برسالة جاهزة. ما في تسعير/دفع أونلاين.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class CorporatePlan(models.Model):
    min_employees = models.PositiveIntegerField(_("أقل عدد موظفين"))
    max_employees = models.PositiveIntegerField(
        _("أكثر عدد موظفين"), null=True, blank=True,
        help_text=_("اتركه فاضي للشريحة المفتوحة (مثال: 50+)."),
    )
    price_per_employee_jod = models.DecimalField(
        _("سعر الموظف (د.أ)"), max_digits=6, decimal_places=2
    )
    meal_type = models.ForeignKey(
        "menu.MealType", on_delete=models.PROTECT, verbose_name=_("نوع الوجبة")
    )
    description = models.TextField(_("الوصف"), blank=True)

    class Meta:
        ordering = ["min_employees"]
        verbose_name = _("خطة شركات")
        verbose_name_plural = _("خطط الشركات")

    def __str__(self):
        return f"{self.employee_range} موظف — {self.price_per_employee_jod} د.أ/موظف"

    @property
    def employee_range(self) -> str:
        if self.max_employees:
            return f"{self.min_employees}-{self.max_employees}"
        return f"{self.min_employees}+"


class CorporateInquiry(models.Model):
    company_name = models.CharField(_("اسم الشركة"), max_length=150)
    contact_person = models.CharField(_("الشخص المسؤول"), max_length=120)
    contact_phone = models.CharField(_("رقم التواصل"), max_length=20)
    employee_count = models.PositiveIntegerField(_("عدد الموظفين التقريبي"))
    delivery_location = models.CharField(_("موقع التوصيل"), max_length=200)
    notes = models.TextField(_("ملاحظات"), blank=True)
    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("طلب عرض سعر شركة")
        verbose_name_plural = _("طلبات عروض أسعار الشركات")

    def __str__(self):
        return f"{self.company_name} ({self.employee_count} موظف)"

    def whatsapp_message(self) -> str:
        lines = [
            "طلب عرض سعر للشركات — Low Calories Jordan",
            f"الشركة: {self.company_name}",
            f"الشخص المسؤول: {self.contact_person}",
            f"رقم التواصل: {self.contact_phone}",
            f"عدد الموظفين: {self.employee_count}",
            f"موقع التوصيل: {self.delivery_location}",
        ]
        if self.notes:
            lines.append(f"ملاحظات: {self.notes}")
        return "\n".join(lines)
