from .homepage import get_homepage_context
from .models import Policy, SiteSettings
from .navigation import (
    get_footer_navigation,
    get_full_navigation,
    get_navigation_cta,
    get_primary_navigation,
)


def site_settings(request):
    """
    يخلي {{ site_settings }} + بيانات التنقّل + روابط السياسات متوفرة بكل تمبلت
    بدون تمريرها يدوياً بكل view. كلها من مصادر حقيقة مركزية:
      - site_settings  → SiteSettings (تواصل، هوية، ألوان)
      - nav            → core.navigation (تنقّل الموقع)
      - footer_policies→ Policy (الصفحات القانونية المنشورة)
    """
    ctx = {
        "site_settings": SiteSettings.get_solo(),
        "nav": {
            "primary": get_primary_navigation(request),
            "full": get_full_navigation(request),
            "footer_groups": get_footer_navigation(request),
            "cta": get_navigation_cta(request),
        },
        "footer_policies": Policy.get_footer_policies(),
    }
    ctx["home"] = get_homepage_context(request)
    return ctx
