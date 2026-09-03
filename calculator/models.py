import secrets
import string

from django.db import models
from django.utils.translation import gettext_lazy as _

from plans.models import Plan

_PROGRESS_ALPHABET = string.ascii_uppercase + string.digits


class CalorieCalculation(models.Model):
    GENDER_CHOICES = [("male", _("ذكر")), ("female", _("أنثى"))]
    GOAL_CHOICES = [("loss", _("خسارة وزن")), ("maintain", _("تثبيت الوزن")), ("gain", _("بناء عضل"))]
    ACTIVITY_CHOICES = [
        ("sedentary", _("قليل الحركة (مكتب، بدون رياضة)")),
        ("light", _("نشاط خفيف (رياضة 1-3 أيام بالأسبوع)")),
        ("moderate", _("نشاط متوسط (رياضة 4-5 أيام بالأسبوع)")),
        ("active", _("نشيط (رياضة يومية أو مكثفة 3-4 أيام)")),
        ("very_active", _("نشيط جداً (رياضة مكثفة 6-7 أيام)")),
        ("athlete", _("رياضي محترف أو عمل بدني شاق يومياً")),
    ]

    gender = models.CharField(_("الجنس"), max_length=10, choices=GENDER_CHOICES)
    age = models.PositiveIntegerField(_("العمر"))
    height_cm = models.PositiveIntegerField(_("الطول (سم)"))
    weight_kg = models.PositiveIntegerField(_("الوزن (كغ)"))
    activity_level = models.CharField(_("مستوى النشاط"), max_length=20, choices=ACTIVITY_CHOICES)
    goal = models.CharField(_("الهدف"), max_length=20, choices=GOAL_CHOICES)

    result_calories = models.PositiveIntegerField(_("السعرات الناتجة"), null=True, blank=True)
    result_protein_g = models.PositiveIntegerField(_("بروتين (غ)"), null=True, blank=True)
    result_carbs_g = models.PositiveIntegerField(_("كربوهيدرات (غ)"), null=True, blank=True)
    result_fat_g = models.PositiveIntegerField(_("دهون (غ)"), null=True, blank=True)
    suggested_plan = models.ForeignKey(Plan, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_("الخطة المقترحة"))

    # ---- متابعة التقدّم (اختياري) ----
    customer_phone = models.CharField(_("رقم الهاتف"), max_length=20, blank=True)
    # ⚠️ خصوصية: بيانات الوزن/السعرات حسّاسة. رقم الهاتف لوحده ما يكفي للوصول
    # للسجل (أي حد بيعرف رقم صاحبه بيشوف وزنه). عشان هيك progress_code إلزامي
    # للوصول (مش اختياري) — يُنشأ فقط لو انعبّى رقم الهاتف.
    progress_code = models.CharField(_("كود المتابعة"), max_length=8, blank=True, db_index=True)

    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("نتيجة حاسبة سعرات")
        verbose_name_plural = _("نتائج حاسبة السعرات")

    def __str__(self):
        return f"{self.get_gender_display()} - {self.age} سنة - {self.result_calories} سعرة"

    @staticmethod
    def code_for_phone(phone: str) -> str:
        """
        يرجّع كود المتابعة لهذا الرقم: نفس الكود لو الرقم استُخدم قبل، وإلا
        كود جديد. (كود واحد ثابت لكل رقم عبر كل حساباته.)
        """
        existing = (
            CalorieCalculation.objects.filter(customer_phone=phone)
            .exclude(progress_code="")
            .values_list("progress_code", flat=True)
            .first()
        )
        if existing:
            return existing
        return "".join(secrets.choice(_PROGRESS_ALPHABET) for _ in range(6))
