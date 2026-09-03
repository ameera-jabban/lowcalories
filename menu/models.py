from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords


class MealType(models.Model):
    name_ar = models.CharField(_("الاسم (عربي)"), max_length=50)
    name_en = models.CharField(_("الاسم (إنجليزي)"), max_length=50)
    slug = models.SlugField(_("المُعرّف"), unique=True)
    icon_emoji = models.CharField(_("رمز تعبيري"), max_length=10, blank=True)
    image = models.ImageField(
        _("صورة افتراضية"), upload_to="meal_types/", blank=True, null=True,
        help_text=_("صورة افتراضية لكل خطط هذا النوع اللي ما إلها صورة خاصة."),
    )

    # توزيع الماكروز التقريبي لهذا النوع — يضبطه الأدمن مرة، يظهر على كروت الخطط
    typical_protein_pct = models.PositiveSmallIntegerField(_("بروتين %"), default=40)
    typical_carbs_pct = models.PositiveSmallIntegerField(_("كربوهيدرات %"), default=40)
    typical_fat_pct = models.PositiveSmallIntegerField(_("دهون %"), default=20)

    class Meta:
        verbose_name = _("نوع وجبة")
        verbose_name_plural = _("أنواع الوجبات")

    def __str__(self):
        return self.name  # مُعرّب حسب لغة الطلب (يرجع name_ar افتراضياً)

    @property
    def name(self):
        """يرجع الاسم بلغة الصفحة الحالية تلقائياً (عربي أو إنجليزي)"""
        from core.utils import localized_field
        return localized_field(self, "name")

    @property
    def macro_split(self):
        """قائمة (مفتاح، نسبة) للعرض كشريط ماكروز على كرت الخطة."""
        return [
            ("protein", self.typical_protein_pct),
            ("carbs", self.typical_carbs_pct),
            ("fat", self.typical_fat_pct),
        ]


class WeeklyMenu(models.Model):
    week_start_date = models.DateField(_("تاريخ بداية الأسبوع"), help_text=_("عادة يوم الأحد"))
    is_active = models.BooleanField(
        _("مفعّل"), default=True, db_index=True,
        help_text=_("فعّل هذا المنيو ليظهر بالموقع (يعطل تلقائياً القديم)")
    )

    # Audit Log — تتبع تفعيل/تعطيل وتعديل المنيو الأسبوعي
    history = HistoricalRecords()

    class Meta:
        ordering = ["-week_start_date"]
        verbose_name = _("منيو أسبوعي")
        verbose_name_plural = _("المنيو الأسبوعي")

    def __str__(self):
        return _("منيو أسبوع %(d)s") % {"d": self.week_start_date}

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_active:
            # يعطل أي منيو ثاني كان مفعّل، عشان يبقى وحد بس فعّال بأي وقت
            WeeklyMenu.objects.exclude(pk=self.pk).update(is_active=False)

    @classmethod
    def get_current(cls):
        return cls.objects.filter(is_active=True).first()


class MenuItem(models.Model):
    DAYS = [
        (0, _("الأحد")), (1, _("الاثنين")), (2, _("الثلاثاء")), (3, _("الأربعاء")),
        (4, _("الخميس")), (5, _("الجمعة")), (6, _("السبت")),
    ]

    weekly_menu = models.ForeignKey(WeeklyMenu, related_name="items", on_delete=models.CASCADE, verbose_name=_("المنيو الأسبوعي"))
    meal_type = models.ForeignKey(MealType, on_delete=models.PROTECT, verbose_name=_("نوع الوجبة"))
    day_of_week = models.IntegerField(_("يوم الأسبوع"), choices=DAYS)
    name_ar = models.CharField(_("الاسم (عربي)"), max_length=120)
    name_en = models.CharField(_("الاسم (إنجليزي)"), max_length=120, blank=True)
    calories = models.PositiveIntegerField(_("السعرات"))
    protein_g = models.PositiveIntegerField(_("بروتين (غ)"))
    carbs_g = models.PositiveIntegerField(_("كربوهيدرات (غ)"))
    fat_g = models.PositiveIntegerField(_("دهون (غ)"))
    image = models.ImageField(_("الصورة"), upload_to="menu/", blank=True)

    # Audit Log — تتبع تعديل وجبات المنيو (سعرات، ماكروز، أسماء)
    history = HistoricalRecords()

    class Meta:
        ordering = ["day_of_week"]
        verbose_name = _("وجبة")
        verbose_name_plural = _("الوجبات")

    def __str__(self):
        return f"{self.name} ({self.get_day_of_week_display()})"

    @property
    def name(self):
        from core.utils import localized_field
        return localized_field(self, "name")
