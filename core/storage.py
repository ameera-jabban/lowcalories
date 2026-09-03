"""
تخزين الملفات الثابتة للإنتاج.

`ForgivingManifestStaticFilesStorage` = نفس سلوك WhiteNoise
(ضغط gzip/brotli + hash بالاسم للـ cache-busting) بس `manifest_strict = False`:
لو انطلب ملف مش موجود بالـ manifest، يرجّع مساره كما هو بدل ما يرمي 500.

السبب: django-jazzmin يستدعي `{% static 'vendor/bootswatch' %}` على مجلد
(مش ملف) في `admin/base.html`، وهذا يكسر `ManifestStaticFilesStorage`
الصارم. الوضع غير الصارم يحل هذا بأمان بدون التأثير على باقي الملفات.
"""
from whitenoise.storage import CompressedManifestStaticFilesStorage


class ForgivingManifestStaticFilesStorage(CompressedManifestStaticFilesStorage):
    manifest_strict = False
