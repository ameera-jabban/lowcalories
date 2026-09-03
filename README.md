# Low Calories Jordan

منصّة اشتراك وجبات صحية في عمّان — **واتساب-أولاً، بدون سلة أو دفع أونلاين**.
كل طلب (اشتراك، استشارة، عرض شركات، إحالة) يُخزَّن في قاعدة البيانات ثم يُحوَّل
إلى واتساب برسالة جاهزة، والفريق يتابع يدوياً.

الموقع ثنائي اللغة بالكامل: **عربي RTL على `/`** و **إنجليزي LTR على `/en/`**.

---

## 1. نظرة عامة على المعمارية

- **Django monolith** — قوالب مُخدَّمة من السيرفر (server-rendered)، لا SPA ولا API عامة.
- **مصدر حقيقة واحد لكل شيء قابل للتغيير**: بيانات التواصل والهوية في `SiteSettings`
  (singleton مع cache)، التنقّل في `core/navigation.py`، محتوى أقسام الصفحة الرئيسية
  في `core/homepage.py` — لا نصوص/أرقام ثابتة في القوالب.
- **CSS/JS مكتوب يدوياً** فوق قوالب Django — بلا Bootstrap/Tailwind build. نظام
  design tokens في `:root` بأعلى `static/css/style.css`.
- **لوحة تحكم Enterprise** على `django-unfold` مع أدوار (RBAC) وتتبّع تعديلات
  (`django-simple-history`).
- **تكامل واتساب** عبر `WhatsApp Business Cloud API` الرسمي (`core/whatsapp_service.py`)
  مع fallback آمن يسجّل في الـ logs بدون توكن.

---

## 2. المكدّس التقني (Tech Stack)

| الطبقة | الأداة |
|---|---|
| Backend | Django 6.1 (متوافق مع `>=5.0,<7.0`)، Python 3.12+ |
| قاعدة البيانات | SQLite للتطوير · PostgreSQL للإنتاج (`psycopg2-binary` + `DATABASE_URL`) |
| القوالب | Django Templates (بدون framework أمامي) |
| الأنماط | CSS/JS يدوي · خطوط Cairo (عربي) + Inter (إنجليزي) من Google Fonts |
| الترجمة | نظام i18n القياسي لـ Django + `scripts/i18n_sync.py` (بديل GNU gettext عبر `polib`) |
| لوحة التحكم | `django-unfold` |
| تتبّع التعديلات | `django-simple-history` |
| الإعدادات | `django-environ` (12-factor — كل قيمة حسّاسة من متغيّر بيئة) |
| الملفات الثابتة | `whitenoise` (ضغط + hash للـ cache-busting، عبر `core.storage.ForgivingManifestStaticFilesStorage`) |
| Cache | LocMem افتراضياً · `django-redis` تلقائياً لو `REDIS_URL` مضبوط |
| WSGI | `gunicorn` للإنتاج |
| تكامل خارجي | WhatsApp Business Cloud API · Meta Pixel (اختياري) · خدمة تقييمات embed (اختياري) |

---

## 3. الميزات الرئيسية (الموجودة فعلياً)

- **خطط الاشتراك والأسعار** — `/plans/` — بطاقات `.mcard` مبنية من `Plan` + `MealType`،
  مجمّعة حسب عدد الأيام، مع خانة كود خصم (عرض استرشادي).
- **مُكوّن الخطة** — `/plans/build/` — تجربة موجّهة (نوع → وجبات/يوم → مدّة) تشتق
  كل التركيبات والأسعار من صفوف `Plan` (لا مصفوفة أسعار مكرّرة)، ملخّص لاصق، ومتابعة عبر واتساب.
- **المنيو الأسبوعي** — `/menu/` — من `WeeklyMenu.get_current()` (منيو مفعّل واحد
  في أي وقت)، تبويبات أيام + شبكة بطاقات.
- **حاسبة السعرات** — `/tools/calorie-calculator/` — حساب Mifflin-St Jeor على
  السيرفر + اقتراح خطة + إمكانية حفظ النتيجة بكود متابعة.
- **متابعة التقدّم** — تبويب داخل «حسابي» للمستخدم المسجّل؛ ولغير المسجّل
  `/tools/my-progress/` (تحقّق برقم الهاتف + كود المتابعة معاً — خصوصية).
- **طلبات استشارة التغذية** — `/consultations/` — نموذج بسيط: العميل يرسل طلب →
  يصل الأدمن → الفريق يتواصل يدوياً. **لا اختيار أخصائي، لا تقويم، لا مواعيد، لا دفع.**
- **طلبات عروض الشركات (B2B)** — `/corporate/` — نموذج (شركة، مسؤول، هاتف،
  عدد موظفين، موقع توصيل) → `CorporateInquiry` + رسالة واتساب.
- **برنامج الإحالة** — `/referral/get-code/` (توليد كود/رابط) و `/r/<code>/`
  (صفحة دعوة الصديق) — مكافأة يوم مجاني للطرفين، يؤكّدها الأدمن.
- **حسابي / بوابة العميل** — `/account/` — تسجيل دخول برقم هاتف + كود دخول
  (بديل مؤقت عن OTP)، تبويبات: نظرة عامة / الاشتراكات / متابعة تقدّمي / بياناتي /
  الإحالة. إدارة الاشتراك (تجميد/استئناف/تغيير نوع الوجبات) — كلها تجهّز رسالة واتساب.
- **أتمتة واتساب** — تأكيد اشتراك تلقائي عند `Subscription` جديد + أوامر
  `send_weekly_reminders` و `send_review_requests`.
- **صفحات قانونية ديناميكية** — `/policies/<slug>/` من `Policy` + `PolicySection`
  (لا تُنشر إلا بعد إضافة نص معتمد).
- **تعدّد اللغات** — عربي/إنجليزي كامل، RTL/LTR، مع إبقاء القيم التقنية (هاتف،
  إيميل، أكواد، تواريخ ISO) اتجاهها LTR عبر أداة `.ltr-value`.
- **لوحة تحكم** — إدارة كل ما سبق بلا كود (أنظر §8).

---

## 4. بنية المشروع

```
lowcalories/
├── lowcalories/       # settings, urls, wsgi/asgi
├── core/              # SiteSettings (singleton) · الصفحة الرئيسية · navigation.py · homepage.py
│                      #   · whatsapp_service.py · audit.py · unfold_conf.py · admin_dashboard.py
│                      #   · middleware.py (AdminLocaleMiddleware) · storage.py
├── menu/              # MealType · WeeklyMenu · MenuItem
├── plans/             # Plan · DeliveryArea · DiscountCode · مُكوّن الخطة (builder)
├── calculator/        # CalorieCalculation · حاسبة السعرات · متابعة التقدّم العامة
├── leads/             # Lead — تسجيل كل ضغطة زر واتساب (صفحة، خطة، كود خصم)
├── accounts/          # Customer · Subscription · بوابة العميل + signals + review
├── corporate/         # CorporatePlan · CorporateInquiry
├── consultations/     # ConsultationRequest (تدفّق بسيط)
├── referrals/         # ReferralCode · Referral
├── templates/         # كل صفحات HTML + templates/core/icons/*.svg + templates/admin/*
├── static/css,js      # style.css · main.js · plan-builder.js · discount.js · admin/css/*
├── locale/en/LC_MESSAGES/  # django.po / django.mo (تُدار عبر scripts/i18n_sync.py)
├── scripts/i18n_sync.py    # مزامنة وتجميع الترجمات بدون GNU gettext
├── seed_data.py            # بيانات تجريبية — استبدلها بالحقيقية قبل النشر
├── .env.example · DEPLOYMENT.md
```

---

## 5. التشغيل المحلي للتطوير

```bash
cd lowcalories

# 1. بيئة افتراضية + المكتبات
python -m venv .venv && source .venv/bin/activate      # ويندوز: .venv\Scripts\activate
pip install -r requirements.txt

# 2. ملف البيئة (ضروري: بدونه DEBUG=False و runserver لا يخدم media/)
cp .env.example .env
#   عدّل .env:  DJANGO_DEBUG=True   ويكفي مفتاح SECRET_KEY أي قيمة للتطوير

# 3. قاعدة البيانات + بيانات تجريبية
python manage.py migrate
python manage.py shell < seed_data.py

# 4. الأدوار + (اختياري) مستخدمو تجربة
python manage.py setup_roles
python manage.py seed_admin_users        # ينشئ gm_demo / menu_demo / orders_demo

# 5. حساب مدير عام
python manage.py createsuperuser

# 6. تجميع الترجمات + الملفات الثابتة
python scripts/i18n_sync.py
python manage.py collectstatic --noinput

# 7. التشغيل
python manage.py runserver
```

- الموقع: <http://127.0.0.1:8000/>  ·  لوحة التحكم: <http://127.0.0.1:8000/admin/>
- `healthz/` نقطة فحص صحّة ثابتة بلا بادئة لغة.

> **مستخدمو التجربة** (`seed_admin_users`) — للتطوير فقط، احذفهم قبل الإنتاج:
> `gm_demo` (مدير عام) · `menu_demo` (مسؤول منيو) · `orders_demo` (موظف متابعة طلبات).
> كلمات السر في `accounts` command المصدري.

---

## 6. متغيّرات البيئة

كلها في `.env` (انظر `.env.example`). **لا تضع أي سرّ حقيقي في المستودع.**

| المتغيّر | الوصف |
|---|---|
| `DJANGO_DEBUG` | `True` للتطوير، `False` للإنتاج |
| `DJANGO_SECRET_KEY` | مفتاح عشوائي ≥ 50 حرفاً — **إلزامي في الإنتاج** |
| `DJANGO_ALLOWED_HOSTS` | نطاقاتك مفصولة بفواصل |
| `DATABASE_URL` | `postgres://user:pass@host:5432/db` — لو غير مضبوط يُستخدم SQLite |
| `REDIS_URL` | اختياري — يفعّل cache عبر Redis لو موجود |
| `DJANGO_CONN_MAX_AGE` · `DJANGO_HSTS_SECONDS` · `DJANGO_LOG_LEVEL` | ضبط إنتاج |
| `SITE_BASE_URL` | العنوان المطلق — لبناء الروابط في رسائل واتساب من أوامر الإدارة |
| `WHATSAPP_CLOUD_API_TOKEN` · `WHATSAPP_PHONE_NUMBER_ID` · `WHATSAPP_CLOUD_API_VERSION` | تفعيل إرسال واتساب الفعلي (فارغة = وضع log فقط) |

---

## 7. الترجمة (i18n) و RTL/LTR

- **لغتان**: `ar` (افتراضية، `/`) و `en` (`/en/`) عبر `i18n_patterns(prefix_default_language=False)`.
- **نصوص الواجهة**: `{% trans %}` / `gettext_lazy` — المفتاح بالعربي، الإنجليزي في `locale/en/LC_MESSAGES/django.po`.
- **المحتوى الديناميكي**: حقول `_ar`/`_en` بكل موديل + خاصية `name`/`title` تختار
  حسب اللغة (`core/utils.localized_field`) وترجع للعربي لو `_en` فاضي.
- **البيئة بلا GNU gettext** — بديلها:
  ```bash
  python scripts/i18n_sync.py    # يملأ الترجمات في django.po ويجمّع django.mo عبر polib
  ```
  شغّله بعد إضافة أي نص `{% trans %}` أو `_()` جديد. (القاموس داخل السكربت هو
  **مصدر الحقيقة** — أي اختلاف يُحدَّث، وأي مفتاح غير مستخدم يُحذف.)
- **RTL/LTR**: الاتجاه من `LANGUAGE_BIDI`. استخدم خصائص CSS منطقية
  (`margin-inline`, `inset-inline-start` …). القيم التقنية (هاتف، إيميل، رابط،
  كود، ID، تاريخ ISO) تبقى LTR عبر `class="ltr-value" dir="ltr"` (يعرّف
  `direction: ltr; unicode-bidi: isolate;`) — **لا تطبّقها على نص عربي عادي.**

---

## 8. لوحة التحكم (django-unfold)

- **الثيم**: `django-unfold` — shell حديث، RTL-aware، هوية البراند من `SiteSettings`
  ديناميكياً (`core/unfold_conf.py`: `SITE_HEADER`/`SITE_ICON` كـ callables، لون
  primary = برتقالي البراند). ملف `static/admin/css/admin-rtl.css` يصلح فجوات RTL
  في Unfold (بنطاق `[dir="rtl"]` فقط).
- **الشريط الجانبي مجمّع** حسب الأعمال: نظرة عامة · العملاء والطلبات · الاشتراكات
  والتسعير · المنيو والتغذية · التوصيل · المحتوى والإعدادات · المستخدمون والصلاحيات.
  كل عنصر مقيّد بصلاحية (يختفي لمن لا يملكها).
- **لوحة القيادة** (`core/admin_dashboard.dashboard_callback`): بطاقات مؤشرات
  تشغيلية حقيقية (طلبات جديدة، اشتراكات فعّالة، leads اليوم …) + رسم 7 أيام +
  آخر نشاط الفريق — كلها تحترم صلاحيات المستخدم.
- **مبدّل اللغة** في الـ shell (عربي/English) — يعمل عبر `core.middleware.AdminLocaleMiddleware`
  الذي يحترم كوكي اللغة لمسارات `/admin/`.
- **صفحة «آخر 20 تعديل عبر الموقع»**: `/admin/audit/recent-changes/` (للمدير العام).

### الأدوار (RBAC) — Django Groups

```bash
python manage.py setup_roles      # idempotent
```

| الدور | الصلاحيات |
|---|---|
| **مدير عام** | كل شيء ما عدا إدارة المستخدمين/المجموعات (`auth`) والبنية التحتية |
| **مسؤول منيو** | CRUD على تطبيق `menu` فقط |
| **موظف متابعة طلبات** | قراءة فقط على `leads.Lead` و `calculator.CalorieCalculation` |

> صلاحية singleton في «إعدادات الموقع» محمية فوق صلاحيات Django (لا يمكن إضافة صف ثانٍ).
> إنشاء مستخدم بدور: أضِفه، فعّل `is_staff`، اختر المجموعة — دون صلاحيات فردية.

### تتبّع التعديلات

مفعّل على: `SiteSettings`, `Plan`, `DeliveryArea`, `WeeklyMenu`, `MenuItem`, `Policy`.
تبويب **History** بكل صفحة تعديل + الربط بالمستخدم عبر `simple_history.middleware.HistoryRequestMiddleware`.

---

## 9. تدفّقات الأعمال المهمة

- **الاشتراك**: العميل يختار خطة (أو يبني واحدة) → زر «اطلب/اشترك» يفتح واتساب
  برسالة جاهزة + يُسجَّل `Lead`. الأدمن يؤكّد على واتساب ثم يضيف `Customer`
  (يتولّد `access_code`) و `Subscription` → signal يرسل تأكيداً. العميل يدخل
  `/account/login/` بالرقم + الكود.
- **الاستشارة**: نموذج `/consultations/` → `ConsultationRequest` بحالة `new` →
  الأدمن يراه في «طلبات الاستشارات»، يتواصل، ويحدّث الحالة. رابط «تواصل عبر واتساب»
  جاهز في صفحة الطلب.
- **عرض الشركات**: نموذج `/corporate/` → `CorporateInquiry` + حالة نجاح فيها
  رابط واتساب بتفاصيل الشركة.
- **الإحالة**: صاحب الكود من `/referral/get-code/` → يشارك `/r/<code>/` → الصديق
  يملأ النموذج → `Referral` (`pending`) → الأدمن يعلّمه `redeemed` (أكشن يمدّد
  اشتراك الطرفين يوماً لو فعّال).
- **الوصول للحساب**: رقم هاتف + كود دخول (بديل OTP). لا تسجيل، لا كلمة سر، لا إيميل.

---

## 10. إرشادات التطوير

- **منطق الأعمال خارج القوالب** — القوالب للعرض فقط. التسعير/الخصم/حساب السعرات/
  تحوّلات الحالة لها تنفيذ مرجعي واحد في الـ backend.
- **مصدر حقيقة واحد** — لا تكرّر سعراً أو رقم واتساب أو تسمية حالة عبر
  template/JS/backend/ترجمة. أضِف محتوى الأقسام في `core/homepage.py` (نمط `navigation.py`).
- **أعِد استخدام المكوّنات** — بطاقة `templates/core/_media_card.html` (`.mcard`)،
  أداة `.ltr-value`، تنسيقات `.form-row` المشتركة، الهيدر/الفوتر.
- **حافظ على EN/AR + RTL/LTR + الاستجابة** في كل تغيير.
- **احذف الكود الميت فعلياً** — لا تعليقات على كود قديم، لا مكوّنات مكرّرة.
- بعد تعديل CSS/JS: `collectstatic`. بعد نص ترجمة: `scripts/i18n_sync.py`.
  بعد تغيير موديل: `makemigrations` + `migrate`.

---

## 11. الاختبار / QA

سكربتات تحقّق قائمة على `django.test.Client` و Playwright في مجلّد scratchpad
المحلّي (غير مرفوعة): `verify.py` (RBAC)، `verify_spec1..3.py`، `verify_contact_policies.py`،
`admin_smoke*.py`، وفحوص Playwright بصرية للصفحات المُعاد تصميمها.

الفحوص الأساسية المتاحة دائماً:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run     # لا هجرات ناقصة
python scripts/i18n_sync.py                            # لا msgstr فارغ
```

> لا توجد حزمة `pytest`/`tox` في المشروع حالياً؛ التحقّق يدوي عبر السكربتات أعلاه
> ونتائج `manage.py check`.

---

## 12. ملاحظات النشر

الدليل الكامل في **`DEPLOYMENT.md`** (3 طرق: PaaS / VPS / Docker). النسخة السريعة:

```bash
cp .env.example .env      # اضبط SECRET_KEY, ALLOWED_HOSTS, DATABASE_URL, DEBUG=False
pip install -r requirements.txt
python manage.py migrate
python manage.py setup_roles
python scripts/i18n_sync.py
python manage.py collectstatic --noinput
gunicorn lowcalories.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

- `DEBUG=False` → `runserver` لا يخدم `media/`؛ استخدم nginx / كائن تخزين للوسائط.
- الملفات الثابتة عبر WhiteNoise (`ForgivingManifestStaticFilesStorage` — `manifest_strict=False`).
- HSTS / SSL redirect / secure cookies تُفعَّل تلقائياً عند `DEBUG=False`.
- لتفعيل إرسال واتساب الفعلي: املأ متغيّرات `WHATSAPP_*` (تطبيق Meta + منتج WhatsApp).
  للرسائل خارج نافذة 24 ساعة يلزم **Message Templates** معتمدة من Meta.

---

## قبل الإنتاج — Checklist

- [ ] ارفع اللوجو الرسمي (إعدادات الموقع → `logo`) — PNG/JPG/WebP (لا SVG).
- [ ] `DJANGO_SECRET_KEY` جديد + `DEBUG=False` + `ALLOWED_HOSTS` الحقيقية.
- [ ] `DATABASE_URL` لـ PostgreSQL.
- [ ] رقم واتساب + الأسعار + الخطط + مناطق التوصيل الحقيقية من لوحة التحكم.
- [ ] احذف مستخدمي التجربة (`gm_demo` …) أو غيّر كلمات سرهم.
- [ ] (اختياري) رقم Meta Pixel + خدمة تقييمات + نص السياسات القانونية (لنشرها).
- [ ] `collectstatic` + HTTPS.
