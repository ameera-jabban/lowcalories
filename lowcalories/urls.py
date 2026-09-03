from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from core.views import health_check

urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),  # لتبديل اللغة (زر عربي/English)
    path("leads/", include("leads.urls")),  # مو محتاج ترجمة بالرابط
    path("healthz/", health_check, name="health_check"),  # بدون بادئة لغة — منصات الاستضافة بتحتاجه ثابت
]

# عربي بدون بادئة (mightygainz.com/menu) و English ببادئة /en/ (زي الموقع الأصلي)
urlpatterns += i18n_patterns(
    path("", include("core.urls")),
    path("menu/", include("menu.urls")),
    path("plans/", include("plans.urls")),
    path("tools/", include("calculator.urls")),
    path("corporate/", include("corporate.urls")),
    path("account/", include("accounts.urls")),
    path("consultations/", include("consultations.urls")),
    path("", include("referrals.urls")),  # /referral/get-code/ و /r/<code>/
    prefix_default_language=False,
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
