from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords

from menu.models import MealType


class Plan(models.Model):
    days = models.PositiveIntegerField(help_text="مثال: 20 / 24 / 26")
    meal_type = models.ForeignKey(MealType, on_delete=models.PROTECT)
    meals_per_day = models.PositiveIntegerField(default=1)
    price_jod = models.DecimalField(max_digits=6, decimal_places=2)
    is_popular = models.BooleanField(default=False, help_text="يظهر عليها وسم 'الأكثر شعبية'")

    # Audit Log — الأسعار أهم شي: مين غيّر السعر وإمتى
    history = HistoricalRecords()

    class Meta:
        ordering = ["days", "price_jod"]
        indexes = [models.Index(fields=["days"])]
        verbose_name = "خطة اشتراك"
        verbose_name_plural = "خطط الاشتراك"

    def __str__(self):
        return f"{self.days} يوم - {self.meal_type.name_ar} - {self.meals_per_day} وجبة ({self.price_jod} د)"

    def whatsapp_message(self):
        from django.utils.translation import gettext as _
        return _(
            "مرحبا، أريد الاشتراك في خطة %(days)s يوم - %(type)s %(meals)s وجبة (%(price)s د)"
        ) % {
            "days": self.days,
            "type": self.meal_type.name,
            "meals": self.meals_per_day,
            "price": self.price_jod,
        }


class DeliveryArea(models.Model):
    name_ar = models.CharField(max_length=80)
    name_en = models.CharField(max_length=80, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    history = HistoricalRecords()

    class Meta:
        ordering = ["name_ar"]
        verbose_name = "منطقة توصيل"
        verbose_name_plural = "مناطق التوصيل"

    def __str__(self):
        return self.name_ar

    @property
    def name(self):
        from core.utils import localized_field
        return localized_field(self, "name")


class DiscountCode(models.Model):
    """
    كود خصم لأول اشتراك. ⚠️ عرض السعر المخفّض بصفحة الخطط "استرشادي" فقط —
    الخصم الفعلي يطبّقه الأدمن يدوياً بمحادثة واتساب (ما في دفع أونلاين).
    """
    code = models.CharField("الكود", max_length=30, unique=True, help_text="مثال: WELCOME15")
    discount_percent = models.PositiveIntegerField(
        "نسبة الخصم %", validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    is_active = models.BooleanField("مفعّل", default=True)
    valid_until = models.DateField("صالح حتى", null=True, blank=True, help_text="فاضي = بدون تاريخ انتهاء")
    max_uses = models.PositiveIntegerField("أقصى عدد استخدامات", null=True, blank=True, help_text="فاضي = بدون حد")
    used_count = models.PositiveIntegerField("عدد الاستخدامات", default=0)

    class Meta:
        verbose_name = "كود خصم"
        verbose_name_plural = "أكواد الخصم"

    def __str__(self):
        return f"{self.code} (-{self.discount_percent}%)"

    def is_valid(self) -> bool:
        if not self.is_active:
            return False
        if self.valid_until and timezone.localdate() > self.valid_until:
            return False
        if self.max_uses is not None and self.used_count >= self.max_uses:
            return False
        return True

    def discounted_price(self, price):
        from decimal import Decimal
        factor = Decimal(100 - self.discount_percent) / Decimal(100)
        return (Decimal(price) * factor).quantize(Decimal("0.01"))
