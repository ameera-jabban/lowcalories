"""
طلب استشارة تغذية — تجربة مبسّطة: العميل يعبّي طلب، والفريق يتواصل معه يدوياً
لترتيب الجلسة. ما في اختيار أخصائي، ولا تقويم، ولا مواعيد، ولا دفع أونلاين.
"""
import re

from django.db import models
from django.utils.translation import gettext_lazy as _

# مصدر الطلب — مفيد لمعرفة أي قناة بتحوّل أكتر
SOURCE_CHOICES = [
    ("consultations_page", _("صفحة الاستشارات")),
    ("calculator_upsell", _("بعد حاسبة السعرات")),
    ("other", _("أخرى")),
]


class ConsultationRequest(models.Model):
    class Status(models.TextChoices):
        NEW = "new", _("جديد")
        CONTACTED = "contacted", _("تم التواصل")
        SCHEDULED = "scheduled", _("تم تحديد موعد")
        COMPLETED = "completed", _("تمّت")
        CANCELLED = "cancelled", _("ملغى")

    class ContactMethod(models.TextChoices):
        WHATSAPP = "whatsapp", _("واتساب")
        PHONE = "phone", _("اتصال هاتفي")
        EMAIL = "email", _("بريد إلكتروني")

    full_name = models.CharField(_("الاسم الكامل"), max_length=120)
    phone = models.CharField(_("رقم الموبايل"), max_length=20)
    email = models.EmailField(_("البريد الإلكتروني"), blank=True)
    preferred_contact = models.CharField(
        _("طريقة التواصل المفضّلة"), max_length=12,
        choices=ContactMethod.choices, default=ContactMethod.WHATSAPP,
    )
    goal = models.CharField(_("الهدف / سبب الاستشارة"), max_length=200)
    notes = models.TextField(_("ملاحظات إضافية"), blank=True)

    language = models.CharField(_("اللغة"), max_length=5, blank=True, editable=False)
    source = models.CharField(
        _("المصدر"), max_length=30, choices=SOURCE_CHOICES,
        default="consultations_page", editable=False,
    )
    status = models.CharField(
        _("الحالة"), max_length=12, choices=Status.choices, default=Status.NEW
    )
    admin_notes = models.TextField(_("ملاحظات داخلية (للفريق فقط)"), blank=True)
    created_at = models.DateTimeField(_("تاريخ الطلب"), auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("طلب استشارة")
        verbose_name_plural = _("طلبات الاستشارات")

    def __str__(self):
        return f"#{self.pk} — {self.full_name}"

    @property
    def reference(self) -> str:
        return f"#{self.pk}"

    @property
    def whatsapp_url(self) -> str:
        """رابط wa.me لرقم العميل — لزر 'تواصل عبر واتساب' بلوحة التحكم."""
        digits = re.sub(r"\D", "", self.phone or "")
        return f"https://wa.me/{digits}" if len(digits) >= 8 else ""
