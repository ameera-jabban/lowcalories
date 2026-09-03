"""
إعدادات مشروع Low Calories Jordan
مبنية بنمط 12-factor: كل إعداد حساس أو بيتغيّر بين بيئات (dev/staging/production)
يُقرأ من متغيرات البيئة (.env محلياً، أو Environment Variables الحقيقية بالسيرفر/PaaS)
بدل ما يكون مكتوب Hardcoded بالكود.
"""
import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DJANGO_DEBUG=(bool, False),
)
# يقرأ ملف .env لو موجود (بيئة محلية/سيرفر تقليدي). بالـ PaaS (Render, Railway, Heroku...)
# عادة بتحط متغيرات البيئة مباشرة من لوحة التحكم تبعهم، فما تحتاج ملف .env أصلاً.
environ.Env.read_env(BASE_DIR / ".env")

# =========================================================================
# الأمان الأساسي
# =========================================================================
SECRET_KEY = env("DJANGO_SECRET_KEY", default="django-insecure-CHANGE-ME-BEFORE-PRODUCTION")
DEBUG = env.bool("DJANGO_DEBUG", default=False)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

# لو الموقع وراء reverse proxy (nginx, Render, Railway...) بيرسل X-Forwarded-Proto
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

INSTALLED_APPS = [
    # لوحة التحكم — django-unfold (لازم قبل django.contrib.admin عشان يستبدل القوالب)
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.simple_history",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "simple_history",  # Audit Log — يتتبع مين عدّل وشو وإمتى
    # تطبيقات المشروع
    "core",
    "menu",
    "plans",
    "calculator",
    "leads",
    "accounts",   # بوابة العميل: تسجيل دخول بالهاتف + إدارة الاشتراك
    "corporate",  # خطط الشركات (B2B) + طلبات عروض الأسعار
    "consultations",  # طلب استشارة تغذية (الفريق يتواصل يدوياً)
    "referrals",   # برنامج الإحالة (كود/رابط لكل عميل)
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # يخدم الملفات الثابتة بكفاءة بدون nginx منفصل
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",  # لازم قبل CommonMiddleware عشان الترجمة تشتغل
    "core.middleware.AdminLocaleMiddleware",  # كوكي اللغة لـ /admin/ (مش تحت i18n_patterns)
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # يربط كل تعديل بتاريخ history بالمستخدم اللي عمله (لـ django-simple-history)
    "simple_history.middleware.HistoryRequestMiddleware",
]

ROOT_URLCONF = "lowcalories.urls"

# تسجيل دخول Django (لوحة التحكم/الطاقم فقط — بوابة العميل تستخدم session خاص).
# الافتراضي /accounts/profile/ غير موجود بالمشروع، فنوجّه للوحة التحكم.
LOGIN_URL = "admin:login"
LOGIN_REDIRECT_URL = "/admin/"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.site_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "lowcalories.wsgi.application"

# =========================================================================
# قاعدة البيانات
# =========================================================================
# محلياً بدون أي إعداد: SQLite تلقائياً (سهل للتجربة).
# بالإنتاج: حط DATABASE_URL بمتغيرات البيئة، مثال:
#   DATABASE_URL=postgres://user:password@host:5432/dbname
DATABASES = {
    "default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")
}
# يخلي الاتصال بقاعدة البيانات يتفتح مرة وينعاد استخدامه (بدل ما ينفتح من جديد كل طلب)
DATABASES["default"]["CONN_MAX_AGE"] = env.int("DJANGO_CONN_MAX_AGE", default=60)

# على SQLite (تطوير محلي): نخلي الكتّاب المتزامنين ينتظروا القفل بدل ما يفشلوا
# فوراً بـ "database is locked" — مفيد مثلاً عند حجزين متزامنين لنفس الموعد.
if DATABASES["default"]["ENGINE"].endswith("sqlite3"):
    DATABASES["default"].setdefault("OPTIONS", {})["timeout"] = 20

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# =========================================================================
# اللغة والمنطقة الزمنية
# =========================================================================
LANGUAGE_CODE = "ar"
LANGUAGES = [
    ("ar", "العربية"),
    ("en", "English"),
]
LOCALE_PATHS = [BASE_DIR / "locale"]
TIME_ZONE = "Asia/Amman"
USE_I18N = True
USE_TZ = True

# =========================================================================
# الملفات الثابتة والوسائط
# =========================================================================
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoise: يضغط الملفات (gzip/brotli) ويحط hash بالاسم للـ cache busting تلقائياً.
# هذا كافي لمواقع بحجمك — ما تحتاج CDN منفصل لحد ما يكبر الترافيك كتير.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    # نسخة "متسامحة" من WhiteNoise (manifest_strict=False) — تتحمّل أي أصل
    # يطلبه ثيم الـ admin عبر {% static %} وما يكون بالـ manifest. شوف core/storage.py
    "staticfiles": {"BACKEND": "core.storage.ForgivingManifestStaticFilesStorage"},
}

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"
# 🔴 ملاحظة مهمة: لو نشرت على منصة بملف نظام مؤقت (Heroku, Render's free tier,
# containers بدون volume دائم)، أي صورة يرفعها الأدمن (لوجو، صور منيو) رح تضيع
# عند أي إعادة نشر. الحل: استخدم django-storages + S3/Cloudflare R2 لتخزين
# الوسائط. جاهز نضيفها لو حددت مزوّد الاستضافة.

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =========================================================================
# التخزين المؤقت (Cache)
# =========================================================================
# لو REDIS_URL موجود بمتغيرات البيئة، نستخدم Redis (ضروري لو عندك أكتر من
# worker process — LocMemCache ما بتنشارك بين البروسيسات). وإلا LocMemCache
# كافي (تطوير محلي أو سيرفر بـ worker وحدة).
REDIS_URL = env("REDIS_URL", default="")
if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        }
    }
else:
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

# =========================================================================
# إعدادات أمان تُفعّل تلقائياً بالإنتاج فقط (DEBUG=False)
# =========================================================================
if not DEBUG:
    SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = env.int("DJANGO_HSTS_SECONDS", default=60 * 60 * 24 * 30)  # 30 يوم
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = "same-origin"
    X_FRAME_OPTIONS = "DENY"

# =========================================================================
# Logging — يطبع للـ console (stdout). كل منصات الاستضافة الحديثة
# (Docker, Render, Railway, systemd+journald) بتلتقط stdout تلقائياً كـ logs،
# فما في داعي لملف log منفصل.
# =========================================================================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {"handlers": ["console"], "level": env("DJANGO_LOG_LEVEL", default="INFO")},
    "loggers": {
        "django": {"handlers": ["console"], "level": env("DJANGO_LOG_LEVEL", default="INFO"), "propagate": False},
    },
}

# =========================================================================
# رقم واتساب العام (للروابط wa.me بالموقع) = مصدر حقيقة واحد فقط:
#   SiteSettings.whatsapp_number  (يُدار من لوحة التحكم)
# ما في إعداد رقم واتساب بالـ settings/‏.env — عمداً — لتفادي تعدّد المصادر.
# =========================================================================

# =========================================================================
# WhatsApp Business Cloud API (رسمي من Meta) — للأتمتة (تأكيد طلب، تذكير منيو،
# طلب تقييم). شوف core/whatsapp_service.py.
#
# 🔑 اتركهم فاضيين محلياً: الخدمة رح "تسجّل" الرسالة بالـ logs بدل ما تبعتها
#    فعلياً، فالموقع يشتغل بدون حساب Meta Business. عبّيهم بالإنتاج لتفعيل الإرسال.
# =========================================================================
WHATSAPP_CLOUD_API_TOKEN = env("WHATSAPP_CLOUD_API_TOKEN", default="")
WHATSAPP_PHONE_NUMBER_ID = env("WHATSAPP_PHONE_NUMBER_ID", default="")
# نسخة Graph API — قابلة للتعديل لو Meta حدّثت النسخة المدعومة
WHATSAPP_CLOUD_API_VERSION = env("WHATSAPP_CLOUD_API_VERSION", default="v21.0")

# العنوان المطلق للموقع — يُستخدم لبناء روابط داخل رسائل واتساب المُرسَلة من
# أوامر الإدارة (management commands) حيث ما في request نبني منه الرابط.
SITE_BASE_URL = env("SITE_BASE_URL", default="http://127.0.0.1:8000")

# =========================================================================
# لوحة التحكم — django-unfold (ثيم عمليات Enterprise)
# =========================================================================
# `UNFOLD` dict فيه callbacks للهوية (SITE_HEADER/SITE_ICON...) تُقرأ
# ديناميكياً من SiteSettings عند كل طلب — مو hardcoded. الشريط الجانبي
# منظّم بمجموعات أعمال + كل عنصر مقيّد بصلاحية (يخفي ما لا يملكه المستخدم).
# التفاصيل: core/unfold_conf.py
from core.unfold_conf import build_unfold_settings

UNFOLD = build_unfold_settings()
