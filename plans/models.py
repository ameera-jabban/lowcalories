from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from menu.models import MealType


class Plan(models.Model):
    days = models.PositiveIntegerField(_("عدد الأيام"), help_text=_("مثال: 20 / 24 / 26"))
    meal_type = models.ForeignKey(MealType, on_delete=models.PROTECT, verbose_name=_("نوع الوجبة"))
    meals_per_day = models.PositiveIntegerField(_("وجبات باليوم"), default=1)
    price_jod = models.DecimalField(_("السعر (د.أ)"), max_digits=6, decimal_places=2)
    is_popular = models.BooleanField(_("الأكثر طلباً"), default=False, help_text=_("يظهر عليها وسم 'الأكثر شعبية'"))
    image = models.ImageField(
        _("صورة خاصة بالخطة"), upload_to="plans/", blank=True, null=True,
        help_text=_("صورة خاصة بهذه الخطة تحديداً. لو فاضية نستخدم صورة نوع الوجبة."),
    )

    # Audit Log — الأسعار أهم شي: مين غيّر السعر وإمتى
    history = HistoricalRecords()

    class Meta:
        ordering = ["days", "price_jod"]
        indexes = [models.Index(fields=["days"])]
        verbose_name = _("خطة اشتراك")
        verbose_name_plural = _("خطط الاشتراك")

    def __str__(self):
        return _("%(days)s يوم · %(type)s · %(meals)s وجبة/يوم · %(price)s د.أ") % {
            "days": self.days, "type": self.meal_type.name,
            "meals": self.meals_per_day, "price": self.price_jod,
        }

    def get_card_image_url(self):
        """
        رابط صورة بطاقة الخطة حسب الأولوية:
          1) صورة الخطة نفسها (Plan.image)
          2) صورة نوع الوجبة الافتراضية (MealType.image)
          3) None — يتركها لبديل التدرّج في core/_media_card.html
        """
        for candidate in (self.image, getattr(self.meal_type, "image", None)):
            try:
                if candidate and candidate.url:
                    return candidate.url
            except (ValueError, AttributeError):
                pass
        return None

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
    name_ar = models.CharField(_("الاسم (عربي)"), max_length=80)
    name_en = models.CharField(_("الاسم (إنجليزي)"), max_length=80, blank=True)
    is_active = models.BooleanField(_("مفعّلة"), default=True, db_index=True)

    history = HistoricalRecords()

    class Meta:
        ordering = ["name_ar"]
        verbose_name = _("منطقة توصيل")
        verbose_name_plural = _("مناطق التوصيل")

    def __str__(self):
        return self.name

    @property
    def name(self):
        from core.utils import localized_field
        return localized_field(self, "name")


class DiscountCode(models.Model):
    """
    كود خصم لأول اشتراك. ⚠️ عرض السعر المخفّض بصفحة الخطط "استرشادي" فقط —
    الخصم الفعلي يطبّقه الأدمن يدوياً بمحادثة واتساب (ما في دفع أونلاين).
    """
    code = models.CharField(_("الكود"), max_length=30, unique=True, help_text=_("مثال: WELCOME15"))
    discount_percent = models.PositiveIntegerField(
        _("نسبة الخصم %"), validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    is_active = models.BooleanField(_("مفعّل"), default=True)
    valid_until = models.DateField(_("صالح حتى"), null=True, blank=True, help_text=_("فاضي = بدون تاريخ انتهاء"))
    max_uses = models.PositiveIntegerField(_("أقصى عدد استخدامات"), null=True, blank=True, help_text=_("فاضي = بدون حد"))
    used_count = models.PositiveIntegerField(_("عدد الاستخدامات"), default=0)

    class Meta:
        verbose_name = _("كود خصم")
        verbose_name_plural = _("أكواد الخصم")

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
