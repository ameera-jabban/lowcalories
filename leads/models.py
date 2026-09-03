from django.db import models
from django.utils.translation import gettext_lazy as _

from plans.models import DiscountCode, Plan


class Lead(models.Model):
    """
    كل مرة حدا يضغط زر واتساب من أي مكان بالموقع، نسجل هون.
    هذا بيعطيك بيانات حقيقية: أي خطة الأكثر طلباً، أي صفحة بتحوّل أكتر.
    """
    plan = models.ForeignKey(Plan, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_("الخطة"))
    source_page = models.CharField(
        _("صفحة المصدر"), max_length=100, help_text=_("مثلاً: plans_page, calculator, home_hero")
    )
    discount_code = models.ForeignKey(
        DiscountCode, null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name=_("كود الخصم المستخدم"),
    )
    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("نية شراء (Lead)")
        verbose_name_plural = _("نوايا الشراء (Leads)")

    def __str__(self):
        return f"{self.source_page} - {self.created_at:%Y-%m-%d %H:%M}"
