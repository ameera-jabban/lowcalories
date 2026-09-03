"""Middleware مخصّص للمشروع."""
from django.conf import settings
from django.utils import translation


class AdminLocaleMiddleware:
    """
    لوحة التحكم (/admin/) مش تحت i18n_patterns، فـ LocaleMiddleware يثبّتها على
    اللغة الافتراضية (ar) ويتجاهل كوكي اللغة. هون نحترم كوكي `django_language`
    لمسارات الأدمن فقط — عشان مبدّل اللغة بشريط Unfold يشتغل (عربي/English).

    يُركّب مباشرةً بعد django.middleware.locale.LocaleMiddleware.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self._supported = {code for code, _name in settings.LANGUAGES}

    def __call__(self, request):
        if request.path.startswith("/admin/"):
            lang = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
            if lang in self._supported and lang != translation.get_language():
                translation.activate(lang)
                request.LANGUAGE_CODE = lang
        return self.get_response(request)
