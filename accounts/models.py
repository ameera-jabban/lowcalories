"""
بوابة العميل — تسجيل دخول بالهاتف + متابعة الاشتراك.

⚠️ ملاحظة على المصادقة (مؤقتة):
    ما في نظام OTP/SMS حقيقي هون (يحتاج مزوّد SMS مدفوع — خارج نطاق هالمرحلة).
    بدلاً منه: لكل عميل `access_code` عشوائي ثابت يُنشأ تلقائياً عند الإنشاء،
    يظهر للأدمن جنب اسم العميل، والأدمن يشاركه معه يدوياً (زي كود دعوة).
    لما يصير في مزوّد WhatsApp/SMS OTP حقيقي، نستبدل هالجزء بتحقق فعلي.
"""
from __future__ import annotations

import secrets
import string
from datetime import date, timedelta

from django.db import models
from django.utils.translation import gettext_lazy as _

_CODE_ALPHABET = string.ascii_uppercase + string.digits


def generate_access_code(length: int = 6) -> str:
    """كود وصول عشوائي قصير (بديل مؤقت عن OTP — انظر docstring الموديول)."""
    return "".join(secrets.choice(_CODE_ALPHABET) for _ in range(length))


class Customer(models.Model):
    phone_number = models.CharField(
        _("رقم الهاتف"), max_length=20, unique=True,
        help_text=_("بصيغة دولية بدون + (مثال: 962795551234)"),
    )
    name = models.CharField(_("الاسم"), max_length=120)
    access_code = models.CharField(
        _("كود الدخول"), max_length=12, blank=True,
        help_text=_("يُنشأ تلقائياً. شاركه مع العميل ليدخل بوابته (بديل مؤقت عن OTP)."),
    )
    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("عميل")
        verbose_name_plural = _("العملاء")

    def __str__(self):
        return f"{self.name} ({self.phone_number})"

    def save(self, *args, **kwargs):
        if not self.access_code:
            self.access_code = generate_access_code()
        super().save(*args, **kwargs)

    @property
    def active_subscription(self):
        """آخر اشتراك فعّال (أو الأحدث لو ما في فعّال) — للعرض في البوابة."""
        return (
            self.subscriptions.filter(status=Subscription.Status.ACTIVE).first()
            or self.subscriptions.first()
        )


class Subscription(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", _("فعّال")
        FROZEN = "frozen", _("مجمّد")
        EXPIRED = "expired", _("منتهي")
        CANCELLED = "cancelled", _("ملغى")

    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="subscriptions", verbose_name=_("العميل")
    )
    plan = models.ForeignKey(
        "plans.Plan", on_delete=models.PROTECT, related_name="subscriptions", verbose_name=_("الخطة")
    )
    start_date = models.DateField(_("تاريخ البداية"), default=date.today)
    end_date = models.DateField(_("تاريخ الانتهاء"), blank=True, null=True)
    status = models.CharField(
        _("الحالة"), max_length=12, choices=Status.choices, default=Status.ACTIVE
    )
    frozen_at = models.DateField(
        _("تاريخ التجميد"), blank=True, null=True,
        help_text=_("يُستخدم لتمديد تاريخ الانتهاء بشكل صحيح عند استئناف الاشتراك."),
    )
    review_requested_at = models.DateTimeField(
        _("تاريخ إرسال طلب التقييم"), blank=True, null=True,
        help_text=_("يمنع إرسال طلب تقييم أكثر من مرة (أمر send_review_requests)."),
    )
    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("اشتراك")
        verbose_name_plural = _("الاشتراكات")

    def __str__(self):
        return f"{self.customer.name} — {self.plan} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        # يُحسب تاريخ الانتهاء تلقائياً من عدد أيام الخطة إذا ما تم تحديده
        if self.start_date and not self.end_date and self.plan_id:
            self.end_date = self.start_date + timedelta(days=self.plan.days)
        super().save(*args, **kwargs)

    @property
    def days_remaining(self) -> int:
        if not self.end_date:
            return 0
        return max((self.end_date - date.today()).days, 0)

    @property
    def is_active(self) -> bool:
        return self.status == self.Status.ACTIVE

    @property
    def is_frozen(self) -> bool:
        return self.status == self.Status.FROZEN

    # -- تحولات الحالة --------------------------------------------------- #
    # ملاحظة: التجميد/الاستئناف يحدّثان سجل الاشتراك محلياً (حالة يطلبها العميل
    # ونتتبعها)، لكن التنفيذ الفعلي (إيقاف/استئناف التوصيل، أي فرق سعر) يؤكده
    # الأدمن عبر واتساب — ما في دفع إلكتروني نثق فيه لأتمتة كاملة.
    def freeze(self):
        self.status = self.Status.FROZEN
        self.frozen_at = date.today()
        self.save(update_fields=["status", "frozen_at"])

    def resume(self):
        frozen_days = (date.today() - self.frozen_at).days if self.frozen_at else 0
        if self.end_date and frozen_days > 0:
            self.end_date = self.end_date + timedelta(days=frozen_days)
        self.status = self.Status.ACTIVE
        self.frozen_at = None
        self.save(update_fields=["status", "frozen_at", "end_date"])
