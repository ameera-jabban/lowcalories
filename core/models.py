import re

from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords


class SiteSettings(models.Model):
    """
    إعدادات عامة singleton — سطر واحد بس بقاعدة البيانات، يتعدل من admin.
    """
    brand_name_ar = models.CharField(max_length=100, default="Low Calories Jordan | لو كالوريز")
    brand_name_en = models.CharField(max_length=100, default="Low Calories Jordan")
    tagline_ar = models.CharField(
        max_length=200,
        default="وجبات صحية محسوبة السعرات، توصلك لباب بيتك في عمّان",
    )
    tagline_en = models.CharField(
        max_length=200, default="Calorie-counted healthy meals, delivered in Amman",
    )

    # ===== مصدر الحقيقة الوحيد لكل بيانات التواصل =====
    # رقم واتساب: القيمة الخام كما تُدخل (ممكن تحوي + أو مسافات) — بننضّفها آلياً
    # قبل توليد رابط wa.me عبر الخاصية wa_number / الدالة whatsapp_link.
    # اتركها فاضية لو ما في رقم بعد → كل عناصر واتساب بالموقع بتختفي بأمان (بدون XXXX).
    whatsapp_number = models.CharField(
        max_length=25, blank=True,
        help_text=_(
            "رقم واتساب برمز الدولة (مثال: 962791234567 أو +962 79 123 4567). "
            "يُنظَّف آلياً لتوليد رابط wa.me. اتركه فاضي = تختفي كل عناصر واتساب."
        ),
    )
    whatsapp_display = models.CharField(
        max_length=30, blank=True,
        help_text=_(
            "الصيغة المعروضة للزوار (مثال: +962 79 123 4567). "
            "لو فاضي نعرض الرقم المنسّق آلياً من whatsapp_number."
        ),
    )
    whatsapp_default_message_ar = models.CharField(
        max_length=300, blank=True,
        help_text=_("رسالة مبدئية تُملأ في واتساب عند الضغط على أي زر عام (اختياري)."),
    )
    whatsapp_default_message_en = models.CharField(max_length=300, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    instagram_url = models.URLField(
        blank=True, default="https://www.instagram.com/lowcalories_jor/",
        help_text=_("رابط صفحة إنستغرام كامل. اتركه فاضي = يختفي أيقونة إنستغرام."),
    )
    instagram_username = models.CharField(
        max_length=60, blank=True,
        help_text=_("اسم المستخدم بدون @ (اختياري — للعرض النصي فقط)."),
    )
    location_ar = models.CharField(
        max_length=160, blank=True, default="عمّان، الأردن",
        help_text=_("الموقع كما يظهر بالفوتر وصفحات السياسات (مثال: عمّان، الأردن)."),
    )
    location_en = models.CharField(max_length=160, blank=True, default="Amman, Jordan")
    support_email = models.EmailField(
        blank=True,
        help_text=_("بريد الدعم/التواصل (يظهر بصفحات السياسات إذا معبّأ)."),
    )
    app_store_url = models.URLField(blank=True)
    google_play_url = models.URLField(blank=True)

    google_rating = models.DecimalField(max_digits=2, decimal_places=1, default=5.0)
    reviews_count = models.PositiveIntegerField(default=0)
    reviews_embed_code = models.TextField(
        blank=True,
        help_text=(
            "الصق هون كود الـ embed تبع أي خدمة تقييمات خارجية (ReputationHub، Elfsight، "
            "أو iframe تقييمات Google مباشرة). إذا تركته فاضي، الموقع بيعرض تلقائياً "
            "التقييمات اليدوية (Testimonials) بدلاً منه."
        ),
    )

    facebook_pixel_id = models.CharField(
        max_length=30, blank=True,
        help_text=_("رقم Meta/Facebook Pixel (بدون حروف). لو فاضي، ما رح ينحقن أي كود تتبع بالموقع."),
    )

    logo = models.ImageField(upload_to="branding/", blank=True)
    hero_image = models.ImageField(
        upload_to="branding/", blank=True,
        help_text=_("صورة الـ Hero بالصفحة الرئيسية. لو فاضية، يظهر رسم توضيحي بألوان الهوية."),
    )
    hero_image_focus = models.CharField(
        max_length=30, blank=True, default="center center",
        help_text=_("نقطة تركيز قص صورة الـ Hero (object-position)، مثال: center center أو 60% 40%."),
    )
    hero_video_url = models.URLField(
        blank=True,
        help_text=_(
            "رابط فيديو mp4 للـ Hero (اختياري). لو معبّأ يُعرض بدل الصورة (صامت، تلقائي، "
            "مع احترام تفضيل تقليل الحركة). صورة الـ Hero تصير poster."
        ),
    )

    # سطر ثقة تحت زر الـ Hero — نص صادق فقط. لو فاضي: نعرض عدد مناطق التوصيل
    # الفعلي، أو تقييم Google لو reviews_count > 0. ما نخترع أرقام.
    hero_stat_ar = models.CharField(max_length=120, blank=True, help_text=_("مثال: نوصّل يومياً داخل عمّان"))
    hero_stat_en = models.CharField(max_length=120, blank=True)

    # ---- تُعرض بالفوتر فقط لو معبّأة (مبدأ: لا نص ثابت بالفوتر) ----
    working_hours_ar = models.CharField(
        max_length=120, blank=True, help_text=_("مثال: يومياً ٩ ص – ٩ م (يظهر بالفوتر إذا معبّأ)"),
    )
    working_hours_en = models.CharField(max_length=120, blank=True)
    privacy_policy_url = models.URLField(blank=True, help_text=_("رابط سياسة الخصوصية (يظهر بالفوتر إذا معبّأ)"))
    terms_url = models.URLField(blank=True, help_text=_("رابط الشروط والأحكام (يظهر بالفوتر إذا معبّأ)"))

    # ---- ألوان الهوية البصرية (قابلة للتعديل من لوحة التحكم مباشرة) ----
    # القيم الافتراضية = ألوان اللوجو الرسمية.
    primary_color = models.CharField(
        max_length=7, default="#FD7B01",
        help_text=_("اللون البرتقالي الأساسي (أزرار، هيدر، تمييز)"),
    )
    secondary_color = models.CharField(
        max_length=7, default="#00A850",
        help_text=_("اللون الأخضر (لوجو 'Low' بالخط اليدوي، تفاصيل ثانوية)"),
    )
    soft_bg_color = models.CharField(
        max_length=7, default="#FFF3E6",
        help_text=_("لون الخلفية الكريمية الفاتحة (خلفيات السكاشن)"),
    )

    # ---- استشارة أخصائي التغذية (upsell — تُقرأ من هون، مو Hardcoded) ----
    consultation_price_jod = models.DecimalField(
        max_digits=6, decimal_places=2, default=0,
        help_text=_("سعر جلسة استشارة التغذية (د.أ). يُنسخ للحجز وقت إنشائه."),
    )
    consultation_duration_min = models.PositiveIntegerField(
        default=20, help_text=_("مدة جلسة الاستشارة بالدقائق (تظهر بصفحة الاستشارات)."),
    )

    # Audit Log — يسجل كل تعديل على الإعدادات الحساسة (واتساب، ألوان، Pixel...)
    history = HistoricalRecords()

    class Meta:
        verbose_name = _("إعدادات الموقع")
        verbose_name_plural = _("إعدادات الموقع")

    def __str__(self):
        return self.brand_name_ar

    def save(self, *args, **kwargs):
        self.pk = 1  # singleton: يضمن دايماً صف واحد بس
        super().save(*args, **kwargs)
        from django.core.cache import cache
        cache.delete("site_settings")  # لو حدا عدّل الإعدادات، لازم الكاش ينمسح فوراً

    @classmethod
    def get_solo(cls):
        """
        نستخدم cache framework عشان نتجنب استعلام قاعدة بيانات بكل طلب لبيانات
        شبه ثابتة (رقم واتساب، ألوان...). الكاش ينمسح تلقائياً عند أي تعديل (انظر save أدناه).
        """
        from django.core.cache import cache

        cached = cache.get("site_settings")
        if cached is not None:
            return cached
        obj, _ = cls.objects.get_or_create(pk=1)
        cache.set("site_settings", obj, timeout=3600)  # ساعة، وينمسح فوراً لو انعدّل قبلها
        return obj

    # ---- واتساب: مصدر حقيقة واحد، ينظّف الرقم مرة واحدة هون ----
    @property
    def wa_number(self):
        """الرقم المنسَّق للآلة: أرقام فقط، مع رمز الدولة، بدون + أو مسافات أو شرطات."""
        digits = re.sub(r"\D", "", self.whatsapp_number or "")
        return digits

    @property
    def has_whatsapp(self):
        """True فقط لو في رقم واتساب حقيقي صالح (مش placeholder ولا ناقص)."""
        n = self.wa_number
        return bool(n) and len(n) >= 8 and "x" not in (self.whatsapp_number or "").lower()

    @property
    def whatsapp_number_display(self):
        """الصيغة المعروضة للزوار — يدوية إن وُجدت، وإلا +<رقم منسّق>."""
        if not self.has_whatsapp:
            return ""
        if self.whatsapp_display:
            return self.whatsapp_display
        return "+" + self.wa_number

    @property
    def whatsapp_default_message(self):
        from core.utils import localized_field
        return localized_field(self, "whatsapp_default_message")

    def whatsapp_link(self, message=""):
        """
        رابط واتساب موحّد لكل الموقع. يرجّع "" لو ما في رقم صالح
        (عشان القوالب تخفي العنصر بدل ما تعرض رابط مكسور).
        """
        if not self.has_whatsapp:
            return ""
        from urllib.parse import quote
        base = f"https://wa.me/{self.wa_number}"
        text = message or self.whatsapp_default_message
        return f"{base}?text={quote(text)}" if text else base

    @property
    def location(self):
        from core.utils import localized_field
        return localized_field(self, "location")

    @property
    def brand_name(self):
        from core.utils import localized_field
        return localized_field(self, "brand_name")

    @property
    def tagline(self):
        from core.utils import localized_field
        return localized_field(self, "tagline")

    @property
    def working_hours(self):
        from core.utils import localized_field
        return localized_field(self, "working_hours")

    @property
    def hero_stat(self):
        from core.utils import localized_field
        return localized_field(self, "hero_stat")


class Testimonial(models.Model):
    """
    تقييمات عملاء تُدار يدوياً من لوحة التحكم — تظهر تلقائياً لو ما في
    reviews_embed_code معبّى بـ SiteSettings. حل عملي لحد ما يصير عندك
    حساب خدمة تقييمات خارجية فعلي.
    """
    customer_name = models.CharField(max_length=100)
    rating = models.PositiveSmallIntegerField(
        default=5, choices=[(i, f"{i} ⭐") for i in range(1, 6)]
    )
    text_ar = models.TextField()
    text_en = models.TextField(blank=True)
    photo = models.ImageField(_("صورة العميل (اختياري)"), upload_to="testimonials/", blank=True)
    location_ar = models.CharField(_("الموقع (اختياري)"), max_length=80, blank=True)
    location_en = models.CharField(_("الموقع (إنجليزي)"), max_length=80, blank=True)
    plan_label_ar = models.CharField(_("الخطة (اختياري)"), max_length=80, blank=True)
    plan_label_en = models.CharField(_("الخطة (إنجليزي)"), max_length=80, blank=True)
    is_featured = models.BooleanField(_("مميّز (يظهر بالصفحة الرئيسية)"), default=True)
    order = models.PositiveIntegerField(_("الترتيب"), default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "-created_at"]
        verbose_name = _("تقييم عميل")
        verbose_name_plural = _("تقييمات العملاء")

    def __str__(self):
        return f"{self.customer_name} — {self.rating}⭐"

    @property
    def text(self):
        from core.utils import localized_field
        return localized_field(self, "text")

    @property
    def location(self):
        from core.utils import localized_field
        return localized_field(self, "location")

    @property
    def plan_label(self):
        from core.utils import localized_field
        return localized_field(self, "plan_label")

    @property
    def initials(self):
        parts = self.customer_name.split()
        return "".join(p[0] for p in parts[:2]).upper() or "?"


class HeroGoal(models.Model):
    """
    التسمية المتغيّرة تحت عنوان الـ Hero (تتبدّل بـ JS): "خسارة وزن" →
    "بناء عضل" → ... — تُدار من لوحة التحكم بدل ما تكون Hardcoded.
    """
    text_ar = models.CharField(_("النص (عربي)"), max_length=60)
    text_en = models.CharField(_("النص (إنجليزي)"), max_length=60, blank=True)
    order = models.PositiveIntegerField(_("الترتيب"), default=0)
    is_active = models.BooleanField(_("مفعّل"), default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = _("هدف (Hero)")
        verbose_name_plural = _("أهداف الـ Hero المتغيّرة")

    def __str__(self):
        return self.text_ar

    @property
    def text(self):
        from core.utils import localized_field
        return localized_field(self, "text")


class HowItWorksStep(models.Model):
    """خطوات "كيف يعمل" بالصفحة الرئيسية (خطوات مرقّمة تلقائياً حسب الترتيب)."""
    title_ar = models.CharField(_("العنوان (عربي)"), max_length=80)
    title_en = models.CharField(_("العنوان (إنجليزي)"), max_length=80, blank=True)
    text_ar = models.CharField(_("الوصف (عربي)"), max_length=200)
    text_en = models.CharField(_("الوصف (إنجليزي)"), max_length=200, blank=True)
    image = models.ImageField(_("صورة الخطة"), upload_to="how/", blank=True)
    image_focus = models.CharField(
        "نقطة تركيز القص", max_length=30, blank=True, default="center center",
        help_text=_("object-position، مثال: center center أو 50% 30%."),
    )
    order = models.PositiveIntegerField(_("الترتيب"), default=0)
    is_active = models.BooleanField(_("مفعّل"), default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = _("خطوة (كيف يعمل)")
        verbose_name_plural = _("خطوات «كيف يعمل»")

    def __str__(self):
        return self.title_ar

    @property
    def title(self):
        from core.utils import localized_field
        return localized_field(self, "title")

    @property
    def text(self):
        from core.utils import localized_field
        return localized_field(self, "text")


class FAQ(models.Model):
    question_ar = models.CharField(_("السؤال (عربي)"), max_length=200)
    question_en = models.CharField(_("السؤال (إنجليزي)"), max_length=200, blank=True)
    answer_ar = models.TextField(_("الجواب (عربي)"))
    answer_en = models.TextField(_("الجواب (إنجليزي)"), blank=True)
    category_ar = models.CharField(
        "التصنيف (عربي)", max_length=60, blank=True,
        help_text=_("اختياري — للتنظيم المستقبلي (خطط، وجبات، توصيل...). ما يظهر كفلتر إلا لو احتجناه."),
    )
    category_en = models.CharField(_("التصنيف (إنجليزي)"), max_length=60, blank=True)
    order = models.PositiveIntegerField(_("الترتيب"), default=0)
    show_on_homepage = models.BooleanField(_("يظهر بمقتطف الصفحة الرئيسية"), default=True)
    is_published = models.BooleanField(_("منشور"), default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = _("سؤال شائع")
        verbose_name_plural = _("الأسئلة الشائعة (FAQ)")

    def __str__(self):
        return self.question_ar

    @property
    def question(self):
        from core.utils import localized_field
        return localized_field(self, "question")

    @property
    def answer(self):
        from core.utils import localized_field
        return localized_field(self, "answer")

    @property
    def category(self):
        from core.utils import localized_field
        return localized_field(self, "category")


class SiteFeature(models.Model):
    """
    نقاط قوة "ليش تختارنا" بالصفحة الرئيسية — تُدار من لوحة التحكم بدل نص ثابت
    بالقالب. الأيقونة مفتاح، والقالب يرسمها SVG inline (بدون مكتبة أيقونات).
    """
    ICON_CHOICES = [
        ("calories", "سعرات محسوبة"),
        ("delivery", "توصيل يومي"),
        ("variety", "تنوّع المنيو"),
        ("fresh", "طازج"),
        ("support", "دعم ومتابعة"),
    ]
    icon = models.CharField(_("الأيقونة"), max_length=20, choices=ICON_CHOICES, default="calories")
    title_ar = models.CharField(_("العنوان (عربي)"), max_length=80)
    title_en = models.CharField(_("العنوان (إنجليزي)"), max_length=80, blank=True)
    text_ar = models.CharField(_("الوصف (عربي)"), max_length=180)
    text_en = models.CharField(_("الوصف (إنجليزي)"), max_length=180, blank=True)
    order = models.PositiveIntegerField(_("الترتيب"), default=0)
    is_active = models.BooleanField(_("مفعّل"), default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = _("ميزة (ليش تختارنا)")
        verbose_name_plural = _("مزايا (ليش تختارنا)")

    def __str__(self):
        return self.title_ar

    @property
    def title(self):
        from core.utils import localized_field
        return localized_field(self, "title")

    @property
    def text(self):
        from core.utils import localized_field
        return localized_field(self, "text")


# =========================================================================
# نظام السياسات / المحتوى القانوني — مصدر حقيقة واحد، قابل للإدارة من لوحة التحكم
#
# مبدأ أساسي: ما منخترع نص قانوني. الصفحة تُعرض فقط لو is_published=True
#   *و* فيها أقسام فيها محتوى فعلي. السياسة غير الجاهزة → ما إلها رابط
#   بالفوتر ولا صفحة (404) ولا صفحة فاضية.
# =========================================================================
class Policy(models.Model):
    """صفحة سياسة/محتوى قانوني واحدة (خصوصية، شروط، إلخ) — بنية ديناميكية."""

    slug = models.SlugField(
        _("المعرّف بالرابط"), max_length=60, unique=True,
        help_text=_("يظهر بالرابط: /policies/<slug>/ (مثال: privacy, terms)."),
    )
    title_ar = models.CharField(_("العنوان (عربي)"), max_length=140)
    title_en = models.CharField(_("العنوان (إنجليزي)"), max_length=140, blank=True)

    is_published = models.BooleanField(
        _("منشورة"), default=False,
        help_text=_(
            "ما تنشرها إلا بعد ما يتأكد المحتوى القانوني. غير منشورة = "
            "ما إلها رابط بالفوتر ولا صفحة (404)."
        ),
    )
    show_in_footer = models.BooleanField(_("تظهر بروابط الفوتر"), default=True)
    order = models.PositiveIntegerField(_("الترتيب"), default=0)

    version = models.CharField(_("رقم النسخة (اختياري)"), max_length=20, blank=True)
    last_updated = models.DateField(
        _("آخر تحديث"), null=True, blank=True,
        help_text=_("التاريخ اللي يظهر بأعلى الصفحة ('آخر تحديث: ...')."),
    )

    meta_description_ar = models.CharField(_("وصف SEO (عربي)"), max_length=180, blank=True)
    meta_description_en = models.CharField(_("وصف SEO (إنجليزي)"), max_length=180, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    class Meta:
        ordering = ["order", "id"]
        verbose_name = _("سياسة / صفحة قانونية")
        verbose_name_plural = _("السياسات والصفحات القانونية")

    def __str__(self):
        return self.title_ar or self.slug

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("core:policy", kwargs={"slug": self.slug})

    @property
    def title(self):
        from core.utils import localized_field
        return localized_field(self, "title")

    @property
    def meta_description(self):
        from core.utils import localized_field
        return localized_field(self, "meta_description")

    def visible_sections(self):
        """الأقسام المرتّبة اللي فيها محتوى فعلي (عنوان أو نص أو قائمة)."""
        return [s for s in self.sections.all() if s.has_content]

    @property
    def has_content(self):
        return any(s.has_content for s in self.sections.all())

    @property
    def is_live(self):
        """جاهزة للعرض فعلياً: منشورة + فيها محتوى."""
        return self.is_published and self.has_content

    # ---- helpers (أسلوب CMS: مصدر واحد لكل مكان يستهلك السياسات) ----
    @classmethod
    def get_enabled(cls):
        return [p for p in cls.objects.prefetch_related("sections") if p.is_live]

    @classmethod
    def get_footer_policies(cls):
        return [p for p in cls.get_enabled() if p.show_in_footer]

    @classmethod
    def get_by_slug(cls, slug):
        return (
            cls.objects.prefetch_related("sections")
            .filter(slug=slug, is_published=True)
            .first()
        )


class PolicySection(models.Model):
    """قسم داخل سياسة: عنوان + فقرات + قائمة (نقطية أو مرقّمة) — كله اختياري."""

    LIST_NONE, LIST_BULLET, LIST_NUMBER = "none", "bullet", "number"
    LIST_CHOICES = [
        (LIST_NONE, "بدون قائمة"),
        (LIST_BULLET, "قائمة نقطية"),
        (LIST_NUMBER, "قائمة مرقّمة"),
    ]

    policy = models.ForeignKey(Policy, related_name="sections", on_delete=models.CASCADE)
    order = models.PositiveIntegerField(_("الترتيب"), default=0)

    heading_ar = models.CharField(_("عنوان القسم (عربي)"), max_length=160, blank=True)
    heading_en = models.CharField(_("عنوان القسم (إنجليزي)"), max_length=160, blank=True)

    body_ar = models.TextField(_("الفقرات (عربي)"), blank=True, help_text=_("افصل كل فقرة بسطر فارغ."))
    body_en = models.TextField(_("الفقرات (إنجليزي)"), blank=True)

    list_type = models.CharField(_("نوع القائمة"), max_length=10, choices=LIST_CHOICES, default=LIST_NONE)
    list_items_ar = models.TextField(_("عناصر القائمة (عربي)"), blank=True, help_text=_("عنصر واحد بكل سطر."))
    list_items_en = models.TextField(_("عناصر القائمة (إنجليزي)"), blank=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = _("قسم سياسة")
        verbose_name_plural = _("أقسام السياسة")

    def __str__(self):
        return self.heading_ar or f"قسم {self.order}"

    @property
    def heading(self):
        from core.utils import localized_field
        return localized_field(self, "heading")

    @property
    def paragraphs(self):
        from core.utils import localized_field
        raw = localized_field(self, "body")
        return [p.strip() for p in re.split(r"\n\s*\n", raw or "") if p.strip()]

    @property
    def list_items(self):
        from core.utils import localized_field
        raw = localized_field(self, "list_items")
        return [ln.strip() for ln in (raw or "").splitlines() if ln.strip()]

    @property
    def has_content(self):
        # عنوان لحاله مش محتوى — لازم فقرات أو عناصر قائمة فعلية عشان يُعرض القسم
        return bool(self.paragraphs or self.list_items)
