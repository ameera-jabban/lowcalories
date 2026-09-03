"""
مصدر الحقيقة الوحيد للتنقّل في الموقع كامله.

كل عناصر التنقّل (النافبار الديسكتوب، القائمة الكبيرة/الأوفرلاي، قائمة الموبايل،
وأعمدة الفوتر) تُبنى من الهيكل هون. غيّر تسمية/رابط/ظهور/ترتيب عنصر من مكان
واحد → بيتحدّث بكل مكان تلقائياً.

- `url_name`   : اسم مسار Django (namespace:name) — يُحوّل لـ URL وقت الطلب عبر reverse().
                 عنصر بدون url_name = عنصر أب لقائمة فرعية (children) فقط.
- `enabled`    : False = يختفي العنصر تلقائياً من كل مكان (بدون رابط فاضي).
- `order`      : ترتيب العرض (تصاعدي).
- `locations`  : وين يظهر العنصر: "primary" (نافبار)، "menu" (القائمة الكبيرة).
- `requires`   : شرط إضافي — "whatsapp" يعني يظهر فقط لو في رقم واتساب مضبوط.
- `children`   : قائمة فرعية (نفس البنية) — تُدعم بأي عنصر، مش محجوزة لواحد.

الدوال المساعدة (CMS-style):
    get_primary_navigation(request)   → عناصر النافبار الأفقي
    get_full_navigation(request)      → عناصر القائمة الكبيرة (مسطّحة)
    get_navigation_cta(request)       → زر الـ CTA ("شوف الخطط")
    get_footer_navigation(request)    → مجموعات أعمدة الفوتر
"""
from django.urls import NoReverseMatch, reverse
from django.utils.translation import gettext_lazy as _

# ملاحظة: الروابط كلها مسارات موجودة فعلياً بالمشروع — ما في صفحات وهمية.
NAVIGATION = [
    {
        "key": "home",
        "label": _("الرئيسية"),
        "url_name": "core:home",
        "order": 0,
        "locations": ["menu"],
    },
    {
        "key": "plans",
        "label": _("الخطط"),
        "url_name": "plans:plans_list",
        "order": 1,
        "locations": ["primary", "menu"],
    },
    {
        "key": "menu",
        "label": _("المنيو الأسبوعي"),
        "url_name": "menu:menu_list",
        "order": 2,
        "locations": ["primary", "menu"],
    },
    {
        "key": "calculator",
        "label": _("حاسبة السعرات"),
        "url_name": "calculator:calorie_calculator",
        "order": 3,
        "locations": ["primary", "menu"],
    },
    {
        "key": "services",
        "label": _("خدمات"),
        "url_name": None,  # عنصر أب — يفتح قائمة فرعية
        "order": 4,
        "locations": ["primary", "menu"],
        "children": [
            {
                "key": "consultations",
                "label": _("استشارة أخصائي تغذية"),
                "url_name": "consultations:list",
                "order": 0,
            },
            {
                "key": "corporate",
                "label": _("خطط الشركات"),
                "url_name": "corporate:corporate_page",
                "order": 1,
            },
            {
                "key": "referrals",
                "label": _("برنامج الإحالة"),
                "url_name": "referrals:get_code",
                "order": 2,
            },
        ],
    },
    {
        "key": "account",
        # "متابعة تقدّمي" صارت تبويب داخل «حسابي» — مش عنصر تنقّل مستقل.
        "label": _("حسابي"),
        "url_name": "accounts:dashboard",
        "order": 6,
        "locations": ["menu"],
    },
    {
        "key": "faq",
        "label": _("الأسئلة الشائعة"),
        "url_name": "core:faq",
        "order": 8,
        "locations": ["menu"],
    },
    {
        "key": "contact",
        "label": _("تواصل معنا"),
        "url_name": "leads:go_to_whatsapp_general",
        "order": 9,
        "locations": ["menu"],
        "requires": "whatsapp",
        "external": True,  # يفتح واتساب — مش صفحة داخلية
    },
]

CTA = {
    "label": _("شوف الخطط"),
    "url_name": "plans:plans_list",
}

# أعمدة الفوتر — نفس مبدأ المصدر الواحد (تُشير لعناصر التنقّل بمفتاحها + عناصر خاصة)
FOOTER_GROUPS = [
    {
        "key": "quick",
        "title": _("روابط سريعة"),
        "items": ["menu", "plans", "calculator", "faq"],
    },
    {
        "key": "services",
        "title": _("خدمات"),
        "items": ["consultations", "corporate", "referrals", "account"],
    },
]


# --------------------------------------------------------------------------- #
# resolution
# --------------------------------------------------------------------------- #
def _has_whatsapp():
    from core.models import SiteSettings

    return SiteSettings.get_solo().has_whatsapp


def _passes_requirement(item):
    req = item.get("requires")
    if req == "whatsapp":
        return _has_whatsapp()
    return True


def _resolve_url(url_name):
    if not url_name:
        return None
    try:
        return reverse(url_name)
    except NoReverseMatch:
        return None


def _resolve_item(item, request, _depth=0):
    """يحوّل عنصر config لـ dict جاهز للقالب — أو None لو معطّل/رابط مكسور."""
    if not item.get("enabled", True) or not _passes_requirement(item):
        return None

    children = []
    for child in sorted(item.get("children", []), key=lambda c: c.get("order", 0)):
        resolved_child = _resolve_item(child, request, _depth + 1)
        if resolved_child:
            children.append(resolved_child)

    url = _resolve_url(item.get("url_name"))
    # عنصر بدون رابط وبدون أبناء صالحين = ما نعرضه (لا روابط فاضية)
    if url is None and not children and not item.get("external_url"):
        return None

    current_path = request.path if request is not None else ""
    is_active = bool(url) and url != "/" and current_path.startswith(url)
    if url == "/" and request is not None:
        is_active = current_path == url
    if not is_active and children:
        is_active = any(c["is_active"] for c in children)

    return {
        "key": item["key"],
        "label": item["label"],
        "url": url or (children[0]["url"] if children else "#"),
        "has_url": url is not None,
        "children": children,
        "has_children": bool(children),
        "is_active": is_active,
        "external": item.get("external", False),
    }


def _resolve_list(request, location):
    out = []
    for item in sorted(NAVIGATION, key=lambda i: i.get("order", 0)):
        if location not in item.get("locations", []):
            continue
        resolved = _resolve_item(item, request)
        if resolved:
            out.append(resolved)
    return out


def get_primary_navigation(request=None):
    """عناصر النافبار الأفقي على الديسكتوب."""
    return _resolve_list(request, "primary")


def get_full_navigation(request=None):
    """
    عناصر القائمة الكبيرة (الأوفرلاي). مسطّحة: عناصر «خدمات» تنزل كعناصر
    مستقلة بدل ما تكون قائمة فرعية، لتجربة قائمة نظيفة عمودية.
    """
    flat = []
    for item in sorted(NAVIGATION, key=lambda i: i.get("order", 0)):
        if "menu" not in item.get("locations", []):
            continue
        resolved = _resolve_item(item, request)
        if not resolved:
            continue
        if resolved["has_url"]:
            flat.append(resolved)
        # لو عنصر أب (بدون رابط) ننزّل أبناءه مباشرة
        elif resolved["has_children"]:
            flat.extend(resolved["children"])
    return flat


def get_navigation_cta(request=None):
    url = _resolve_url(CTA["url_name"])
    if not url:
        return None
    return {"label": CTA["label"], "url": url}


def get_footer_navigation(request=None):
    """مجموعات أعمدة الفوتر — مبنية من نفس مصدر التنقّل."""
    index = {}

    def _index(items):
        for it in items:
            index[it["key"]] = it
            _index(it.get("children", []))

    _index(NAVIGATION)

    groups = []
    for group in FOOTER_GROUPS:
        links = []
        for key in group["items"]:
            cfg = index.get(key)
            if not cfg:
                continue
            resolved = _resolve_item(cfg, request)
            if resolved and resolved["has_url"]:
                links.append(resolved)
        if links:
            groups.append({"key": group["key"], "title": group["title"], "links": links})
    return groups
