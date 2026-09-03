from django.db import models

from plans.models import DiscountCode, Plan


class Lead(models.Model):
    """
    كل مرة حدا يضغط زر واتساب من أي مكان بالموقع، نسجل هون.
    هذا بيعطيك بيانات حقيقية: أي خطة الأكثر طلباً، أي صفحة بتحوّل أكتر.
    """
    plan = models.ForeignKey(Plan, null=True, blank=True, on_delete=models.SET_NULL)
    source_page = models.CharField(max_length=100, help_text="مثلاً: plans_page, calculator, home_hero")
    discount_code = models.ForeignKey(
        DiscountCode, null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name="كود الخصم المستخدم",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "نية شراء (Lead)"
        verbose_name_plural = "نوايا الشراء (Leads)"

    def __str__(self):
        return f"{self.source_page} - {self.created_at:%Y-%m-%d %H:%M}"
