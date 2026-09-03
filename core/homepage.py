"""
مصدر الحقيقة الوحيد لمحتوى أقسام الصفحة الرئيسية (عناوين، أوصاف، أزرار CTA،
مفاتيح إظهار/إخفاء). نفس فلسفة core/navigation.py:

- النصوص هون قابلة للترجمة (gettext_lazy) — العربي أساسي والإنجليزي من django.po.
- الروابط تُخزَّن كأسماء مسارات Django وتُحوَّل وقت الطلب (reverse) — ما في URL ثابت.
- بيانات الأعمال (خطط، وجبات، تقييمات، خطوات) ما تتكرر هون — تُقرأ من الموديلات.
- كل قسم إله enabled؛ وكل CTA إله enabled — لو مطفّي ما ينعرض ولا فراغ.

الاستهلاك: عبر core.context_processors → {{ home.hero }} ... بكل قالب.
"""
from django.conf import settings
from django.urls import NoReverseMatch, reverse
from django.utils.translation import gettext_lazy as _

# صورة بديلة موحّدة تُستخدم فقط لبطاقات الوجبات (MenuItem) اللي ما إلها صورة مرفوعة
# ولقسم المرونة. بطاقات الخطط ما تستخدمها — تعتمد على Plan.image / MealType.image
# أو بديل التدرّج في _media_card.html.
CARD_FALLBACK_IMAGE = settings.MEDIA_URL.rstrip("/") + "/branding/ChickenSatayBowl.webp"


def _image_url_or_none(image_field):
    """رابط الصورة لو مرفوعة فعلاً، وإلا None (يتركها لبديل التدرّج بالقالب)."""
    try:
        if image_field and image_field.url:
            return image_field.url
    except (ValueError, AttributeError):
        pass
    return None


def _card_image(image_field):
    """لبطاقات الوجبات: رابط الصورة الحقيقية إن وُجدت، وإلا الصورة البديلة الموحّدة."""
    return _image_url_or_none(image_field) or CARD_FALLBACK_IMAGE


def _url(url_name):
    if not url_name:
        return None
    try:
        return reverse(url_name)
    except NoReverseMatch:
        return None


def _cta(conf):
    """يحوّل تعريف CTA لـ dict جاهز — أو None لو مطفّي/رابط مكسور."""
    if not conf or not conf.get("enabled", True):
        return None
    url = _url(conf.get("url_name"))
    if not url:
        return None
    return {"label": conf["label"], "url": url}


# ============================ HERO ============================
HERO = {
    "enabled": True,
    "eyebrow": {
        "enabled": True,
        "text": _("اشتراك وجبات صحية — عمّان، الأردن"),
    },
    # لو headline_text = None: نستخدم site_settings.tagline (المحتوى المعتمد الحالي).
    # highlight = كلمة/عبارة داخل العنوان تتلوّن ببرتقالي الهوية (اختياري).
    "headline_text": None,
    "headline_highlight": None,
    "description": _("سعرات محسوبة، ماكروز مضبوطة، وتوصيل يومي داخل عمّان."),
    "cta": {"enabled": True, "label": _("اطلب الآن"), "url_name": "plans:plans_list"},
    "secondary_cta": {"enabled": True, "label": _("شوف المنيو"), "url_name": "menu:menu_list"},
    "scroll_label": _("انتقل إلى خطط الوجبات"),
    "show_goal_rotator": True,   # يعرض HeroGoal المتغيّرة بعد العنوان لو متوفرة
}


def get_hero(request=None):
    """
    dict جاهز للقالب. الوسائط (صورة/فيديو) والعنوان الافتراضي يجوا من SiteSettings
    عشان يضلّوا يتداروا من لوحة التحكم.
    """
    if not HERO.get("enabled", True):
        return None

    from core.models import HeroGoal, SiteSettings

    s = SiteSettings.get_solo()

    eyebrow = HERO["eyebrow"]["text"] if HERO["eyebrow"].get("enabled") else None
    headline = str(HERO["headline_text"] or s.tagline)

    # تقسيم العنوان حول الكلمة المميّزة (لو مضبوطة وموجودة فيه)
    hl = HERO["headline_highlight"]
    if hl and str(hl) in headline:
        before, _sep, after = headline.partition(str(hl))
        headline_parts = {"before": before, "highlight": str(hl), "after": after}
    else:
        headline_parts = {"before": headline, "highlight": "", "after": ""}

    media = None
    if getattr(s, "hero_video_url", ""):
        media = {
            "type": "video",
            "src": s.hero_video_url,
            "poster": s.hero_image.url if s.hero_image else "",
        }
    elif s.hero_image:
        media = {
            "type": "image",
            "src": s.hero_image.url,
            "focus": s.hero_image_focus or "center center",
        }

    goals = []
    if HERO.get("show_goal_rotator"):
        goals = list(HeroGoal.objects.filter(is_active=True))

    # زر التمرير → قسم الخطط لو موجود، وإلا شريط المزايا (كلاهما ثابت الـ id)
    scroll_target = "#home-meal-plans" if get_meal_plans(request) else "#home-features"

    return {
        "enabled": True,
        "eyebrow": eyebrow,
        "headline": headline,
        "headline_parts": headline_parts,
        "description": HERO["description"],
        "cta": _cta(HERO["cta"]),
        "secondary_cta": _cta(HERO["secondary_cta"]),
        "media": media,
        "goals": goals,
        "scroll_target": scroll_target,
        "scroll_label": HERO["scroll_label"],
    }


# ============================ FAQ ============================
FAQ_SECTION = {
    "enabled": True,
    "title": _("عندك أسئلة؟"),
    "title_line2": _("شوف الأسئلة الشائعة"),
    "allow_multiple_open": False,
    "homepage_limit": 6,
    "support_card": {
        "enabled": True,
        "title": _("عندك سؤال ثاني؟"),
        "description": _("فريقنا جاهز يساعدك — راسلنا على واتساب وبنرد عليك بأسرع وقت."),
        "cta_label": _("تواصل على واتساب"),
        "whatsapp_message": _("مرحبا، عندي سؤال عن Low Calories Jordan"),
        "show_working_hours": True,
    },
}


def get_faq_section(request=None, *, homepage=False):
    """
    قسم الأسئلة الشائعة (يُستخدم بالصفحة الرئيسية كمقتطف + بصفحة /faq كامل).
    الأسئلة من موديل FAQ (مصدر واحد). كرت الدعم يستخدم واتساب المركزي.
    """
    if not FAQ_SECTION.get("enabled", True):
        return None

    from core.models import FAQ, SiteSettings

    qs = FAQ.objects.filter(is_published=True)
    if homepage:
        qs = qs.filter(show_on_homepage=True)[: FAQ_SECTION["homepage_limit"]]
    faqs = list(qs)
    if not faqs:
        return None

    s = SiteSettings.get_solo()
    card_conf = FAQ_SECTION["support_card"]
    support = None
    if card_conf.get("enabled"):
        wa = s.whatsapp_link(str(card_conf["whatsapp_message"])) if s.has_whatsapp else ""
        support = {
            "title": card_conf["title"],
            "description": card_conf["description"],
            "cta_label": card_conf["cta_label"],
            "cta_url": wa,
            "working_hours": s.working_hours if card_conf.get("show_working_hours") else "",
        }

    import json

    jsonld = json.dumps({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": f.question,
                "acceptedAnswer": {"@type": "Answer", "text": f.answer},
            }
            for f in faqs
        ],
    }, ensure_ascii=False).replace("</", "<\\/")

    return {
        "title": FAQ_SECTION["title"],
        "title_line2": FAQ_SECTION["title_line2"],
        "allow_multiple_open": FAQ_SECTION["allow_multiple_open"],
        "faqs": faqs,
        "support": support,
        "is_homepage": homepage,
        "jsonld": jsonld,
    }


# ============================ HOW IT WORKS ============================
HOW_IT_WORKS = {
    "enabled": True,
    "title": _("كيف يعمل؟"),
    "subtitle": _("توصل لهدفك بثلاث خطوات بسيطة."),
    "cta": {"enabled": True, "label": _("شوف الخطط"), "url_name": "plans:plans_list"},
}


def get_how_it_works(request=None):
    if not HOW_IT_WORKS.get("enabled", True):
        return None
    from core.models import HowItWorksStep

    steps = list(HowItWorksStep.objects.filter(is_active=True))
    if not steps:
        return None
    # الترقيم يُحسب تلقائياً من الموضع بعد الفلترة والترتيب (تعطيل خطوة يعيد الترقيم)
    for i, step in enumerate(steps, start=1):
        step.display_number = i
    return {
        "title": HOW_IT_WORKS["title"],
        "subtitle": HOW_IT_WORKS["subtitle"],
        "cta": _cta(HOW_IT_WORKS["cta"]),
        "steps": steps,
    }


# ============================ TESTIMONIALS ============================
TESTIMONIALS = {
    "enabled": True,
    "title": _("نتائج حقيقية، قصص حقيقية"),
    # بيان الثقة: لو في تقييمات موثّقة نعرض رقمها، وإلا جملة معتمدة بدون أرقام مخترعة
    "trust_fallback": _("موثوقون من مجتمع Low Calories"),
    "cta": {"enabled": False, "label": _("شوف الخطط"), "url_name": "plans:plans_list"},
}


def get_testimonials(request=None):
    if not TESTIMONIALS.get("enabled", True):
        return None
    from core.models import SiteSettings, Testimonial

    items = list(Testimonial.objects.filter(is_published=True, is_featured=True))
    if not items:
        return None

    s = SiteSettings.get_solo()
    if s.reviews_count:
        trust = _("★ %(rating)s — %(count)s تقييم") % {
            "rating": s.google_rating, "count": s.reviews_count,
        }
    else:
        trust = TESTIMONIALS["trust_fallback"]

    return {
        "title": TESTIMONIALS["title"],
        "trust": trust,
        "cta": _cta(TESTIMONIALS["cta"]),
        "items": items,
    }


# ============================ MEAL PLANS (carousel) ============================
MEAL_PLANS = {
    "enabled": True,
    "title": _("لاقِ خطتك المثالية"),
    "cta": {"enabled": True, "label": _("شوف كل الخطط"), "url_name": "plans:plans_list"},
}


def get_meal_plans(request=None):
    """
    كروت أنواع الخطط للصفحة الرئيسية — مبنية من MealType + Plan (مصدر واحد).
    كل كرت = نوع خطة فعلي، مع أقل سعر محسوب ديناميكياً وشريط ماكروز حقيقي.
    """
    if not MEAL_PLANS.get("enabled", True):
        return None
    from menu.models import MealType
    from plans.models import Plan

    plans = list(Plan.objects.select_related("meal_type"))
    if not plans:
        return None

    by_type = {}
    for p in plans:
        by_type.setdefault(p.meal_type_id, []).append(p)

    plans_url = _url("plans:plans_list")
    macro_labels = {"protein": _("بروتين"), "carbs": _("كارب"), "fat": _("دهون")}

    rows = []
    for mt in MealType.objects.all():
        mt_plans = by_type.get(mt.id)
        if not mt_plans:
            continue
        popular = any(p.is_popular for p in mt_plans)
        min_price = min(p.price_jod for p in mt_plans)
        # صورة كرت نوع الخطة: صورة النوع الافتراضية، وإلا صورة أول خطة من هذا النوع
        # إلها صورة خاصة، وإلا بديل التدرّج في _media_card.html.
        card_image = _image_url_or_none(getattr(mt, "image", None))
        if not card_image:
            for p in mt_plans:
                card_image = _image_url_or_none(getattr(p, "image", None))
                if card_image:
                    break
        rows.append((popular, min_price, {
            "variant": "plan",
            "href": plans_url,
            "image": card_image,
            "image_alt": mt.name,
            "badge": _("الأكثر طلباً") if popular else None,
            "title": mt.name,
            "macros": [{"key": k, "pct": v} for k, v in mt.macro_split],
            "macro_legend": [
                {"label": macro_labels[k], "value": f"{v}%"} for k, v in mt.macro_split
            ],
            "price_label": _("تبدأ من"),
            "price": min_price,
            "currency": _("د.أ"),
        }))
    if not rows:
        return None

    rows.sort(key=lambda r: (not r[0], r[1]))
    return {
        "title": MEAL_PLANS["title"],
        "min_price": min(p.price_jod for p in plans),
        "cta": _cta(MEAL_PLANS["cta"]),
        "cards": [r[2] for r in rows],
    }


# ============================ WEEKLY MENU (live preview) ============================
WEEKLY_MENU = {
    "enabled": True,
    "title": _("منيو يتجدّد كل أسبوع"),
    "subtitle": _("وجبات طازة محسوبة السعرات، جاهزة لأسبوعك."),
    "benefits": [
        {"enabled": True, "label": _("سعرات محسوبة")},
        {"enabled": True, "label": _("مكوّنات طازة")},
        {"enabled": True, "label": _("خيارات بروتين متعددة")},
        {"enabled": True, "label": _("يتجدّد كل أسبوع")},
    ],
    "cta": {"enabled": True, "label": _("شوف المنيو الكامل"), "url_name": "menu:menu_list"},
    "max_items": 12,
}


def get_weekly_menu_preview(request=None):
    """
    مقتطف حي من المنيو الأسبوعي الفعّال (WeeklyMenu.get_current) — نفس مصدر
    صفحة المنيو. لو تغيّر المنيو الفعّال من لوحة التحكم، هالقسم يتحدّث تلقائياً.
    """
    if not WEEKLY_MENU.get("enabled", True):
        return None
    from menu.models import WeeklyMenu

    menu = WeeklyMenu.get_current()
    if not menu:
        return None
    items = list(menu.items.select_related("meal_type").all()[: WEEKLY_MENU["max_items"]])
    if not items:
        return None

    menu_url = _url("menu:menu_list")
    cards = []
    for m in items:
        legend = []
        if m.protein_g:
            legend.append({"key": "protein", "label": _("بروتين"), "value": _("%(g)sغ") % {"g": m.protein_g}})
        if m.carbs_g:
            legend.append({"key": "carbs", "label": _("كارب"), "value": _("%(g)sغ") % {"g": m.carbs_g}})
        if m.fat_g:
            legend.append({"key": "fat", "label": _("دهون"), "value": _("%(g)sغ") % {"g": m.fat_g}})
        cards.append({
            "variant": "meal",
            "layout": "stacked",
            "href": menu_url,
            "image": _card_image(m.image),
            "image_alt": m.name,
            "badge": _("%(c)s سعرة") % {"c": m.calories} if m.calories else None,
            "category": m.meal_type.name if m.meal_type else "",
            "title": m.name,
            "macro_legend": legend,
        })

    return {
        "title": WEEKLY_MENU["title"],
        "subtitle": WEEKLY_MENU["subtitle"],
        "benefits": [b["label"] for b in WEEKLY_MENU["benefits"] if b.get("enabled", True)],
        "cta": _cta(WEEKLY_MENU["cta"]),
        "cards": cards,
        "week_start": menu.week_start_date,
    }


# ============================ FLEXIBILITY (split section) ============================
FLEX_SECTION = {
    "enabled": True,
    "heading_line1": _("تحكّم كامل."),
    "heading_line2": _("مرونة تامّة."),
    "benefits": [
        _("سعرات وماكروز تناسب هدفك بالضبط."),
        _("اختر يلي بتحبه، وبدّل يلي ما بتحبه."),
    ],
    "highlight_title": _("جمّد. تخطَّ. غيّر. وقت ما بدك."),
    "highlight_text": _(
        "حياتك بتتغيّر وخطتك بتتغيّر معك — عدّل لحد ٢٤ ساعة قبل التوصيل بدون أي تعقيد."
    ),
    "preview": {
        "question": _("أي أيام بتحب توصلك وجبات Low Calories؟"),
        "day_labels": [_("أحد"), _("إثنين"), _("ثلاثاء"), _("أربعاء"), _("خميس"), _("جمعة"), _("سبت")],
        "selected_days": [0, 1, 4, 5, 6],   # عرض بصري فقط
        "skipped_day": 3,
        "address_label": _("العنوان"),
        "address_value": _("البيت"),
        "time_label": _("الوقت"),
        "time_value": _("٧ ص – ١١ ص"),
        "skipped_text": _("التوصيل متخطّى ليوم الأربعاء"),
    },
}


def get_flex_section(request=None):
    if not FLEX_SECTION.get("enabled", True):
        return None
    from core.models import SiteSettings

    s = SiteSettings.get_solo()
    image = s.hero_image.url if s.hero_image else CARD_FALLBACK_IMAGE

    pv = FLEX_SECTION["preview"]
    days = [
        {"label": lbl, "selected": i in pv["selected_days"], "skipped": i == pv["skipped_day"]}
        for i, lbl in enumerate(pv["day_labels"])
    ]
    return {
        "heading_line1": FLEX_SECTION["heading_line1"],
        "heading_line2": FLEX_SECTION["heading_line2"],
        "benefits": FLEX_SECTION["benefits"],
        "highlight_title": FLEX_SECTION["highlight_title"],
        "highlight_text": FLEX_SECTION["highlight_text"],
        "image": image,
        "preview": {
            "question": pv["question"],
            "days": days,
            "address_label": pv["address_label"], "address_value": pv["address_value"],
            "time_label": pv["time_label"], "time_value": pv["time_value"],
            "skipped_text": pv["skipped_text"],
        },
    }


def get_homepage_context(request=None):
    return {
        "hero": get_hero(request),
        "meal_plans": get_meal_plans(request),
        "flex": get_flex_section(request),
        "weekly_menu": get_weekly_menu_preview(request),
        "how": get_how_it_works(request),
        "testimonials": get_testimonials(request),
        "faq": get_faq_section(request, homepage=True),
    }
