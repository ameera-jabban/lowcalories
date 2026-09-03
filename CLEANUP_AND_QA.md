# Cleanup & QA Reports

تقارير التنظيف والتحقّق للتغييرات الكبيرة (إزالة المدونة، تبسيط الاستشارات،
تدقيق التعريب). تاريخ آخر تحديث: 2026-09-03.

---

## 1. تقرير تنظيف الاستشارات (Nutritionist Consultation → Consultation Request)

**الهدف:** تبسيط التدفّق إلى: العميل يرسل طلب → يصل الأدمن → الفريق يتواصل يدوياً.
**حُذف بالكامل:** اختيار أخصائي، ملفات الأخصائيين، المواعيد المتاحة، التقويم،
حجز الفترات الزمنية، معالج الحجز.

### كود مُزال (فيزيائياً، مش مُعلَّق)

| ماذا | أين |
|---|---|
| موديلات `Nutritionist` · `ConsultationSlot` · `ConsultationBooking` | `consultations/models.py` (أُعيد كتابته كاملاً → `ConsultationRequest` + `SOURCE_CHOICES` فقط) |
| Views: قوائم الأخصائيين · صفحة `book` · أكشن `generate_slots` · منطق القفل `select_for_update` | `consultations/views.py` (أُعيد كتابته → دالة واحدة `consultations_list`) |
| Forms: `ConsultationBookingForm` | `consultations/forms.py` (أُعيد كتابته → `ConsultationRequestForm`) |
| Admin: `NutritionistAdmin` · `ConsultationSlotAdmin` · `ConsultationBookingAdmin` · أكشن «توليد أسبوع مواعيد» | `consultations/admin.py` (أُعيد كتابته → `ConsultationRequestAdmin` فقط) |
| قوالب: `templates/consultations/book.html` · `templates/admin/consultations/generate_slots.html` · مجلد `templates/admin/consultations/` | محذوفة |
| مسار URL `consultations:book` (كان `book/<slot_id>/`) | محذوف — الآن `consultations/urls.py` فيه مسار واحد فقط |

### الهجرات (migrations)

- `consultations/0003_consultation_request_flow.py` — كُتبت يدوياً (autodetector فشل):
  `AlterUniqueTogether(consultationslot, set())` ثم `DeleteModel` ×3 (Booking / Slot /
  Nutritionist) ثم `CreateModel(ConsultationRequest)`.
- `0001_initial.py` و `0002_nutritionist_name_localized.py` **مُحتفَظ بهما** — تاريخ
  الهجرات لا يُعاد كتابته؛ `0003` هي التي تحذف الموديلات القديمة. تشغيل `migrate`
  من الصفر يُنشئ ثم يحذف بأمان.

### منطق أعمال مُزال

- منع الحجز المزدوج (transaction + row lock) — لم يعد له معنى (لا مواعيد).
- نسخ السعر وقت الحجز (`price_jod` ثابت على `ConsultationBooking`) — أُزيل.
  السعر الآن **عرض فقط** من `SiteSettings.consultation_price_jod`.

### كود مُحتفَظ به + السبب

- `SiteSettings.consultation_price_jod` / `consultation_duration_min` — **يُبقى**:
  يُعرَض في صفحة الاستشارة كـ «رسوم الاستشارة» (بلوك خفيف). حذفه يتطلب migration
  على `core` بلا فائدة.
- `SOURCE_CHOICES` (`consultations_page` / `calculator_upsell` / `other`) — يُبقى:
  يميّز قناة التحويل (`ConsultationRequest.source`).
- upsell الحاسبة — يُبقى لكن مبسّط: زر `class="btn btn-secondary"` يوصل
  `consultations:list?source=calculator_upsell` (كان بانر مشروط بتوفّر موعد).

### مفاتيح ترجمة مُزالة

- سلاسل واجهة الحجز القديمة (اختيار الأخصائي، «المواعيد المتاحة»، «الموعد مؤكّد»،
  نصوص الفترات الزمنية) — حُذفت من `scripts/i18n_sync.py` ويُقلِّمها `main()` من `.po`.
- **متبقٍّ متعمّد:** `"استشارة أخصائي تغذية" → "Nutritionist Consultation"` (عنوان
  الصفحة الفعلي) وترجمات فيها كلمة "nutritionist" ضمن جُمَل إنجليزية صحيحة — ليست كوداً ميتاً.

### تبعيات

لا تبعيات أُضيفت أو أُزيلت (ما في مكتبة تقويم/حجز كانت مستخدمة).

### نتائج البناء/الاختبار

`manage.py check` نظيف · `verify_spec2.py` أُعيد كتابته للتدفّق الجديد (42/42) ·
لا هجرات ناقصة.

---

## 2. تقرير إزالة المدونة (Blog)

**الهدف:** إزالة ميزة المدونة فيزيائياً من كل مكان يخصّها حصرياً.

### مُزال

| ماذا | أين |
|---|---|
| تطبيق `blog/` كامل (models, views, admin, urls, templates, migrations) | مجلد `blog/` محذوف بالكامل |
| جداول قاعدة البيانات (`BlogPost`) | `python manage.py migrate blog zero` قبل حذف المجلد |
| `"blog"` من `INSTALLED_APPS` | `lowcalories/settings.py` |
| `path("blog/", include("blog.urls"))` | `lowcalories/urls.py` |
| `from blog.models import BlogPost` + سياق `guides` | `core/views.py` (`home()` تُرجع الآن `{popular_plan, hero_stat}` فقط) |
| عنصر تنقّل «المدونة» + مجموعة فوتر تحويه | `core/navigation.py` |
| `<li>` المدونة في الفوتر | `templates/base.html` |
| بذرة `BlogPost` + الاستيراد | `seed_data.py` |
| إعدادات jazzmin للمدونة (`order_with_respect_to`, `icons`) | كان `core/jazzmin_conf.py` (لاحقاً حُذف الملف كله بهجرة Unfold) |
| صلاحيات المدونة من دور «مسؤول منيو» | `core/management/commands/setup_roles.py` |
| 2 contenttypes + 8 صلاحيات `blog.*` | حُذفت يدوياً عبر سكربت `python -c` (`remove_stale_contenttypes` رفض الـ pipe) |
| قوالب `templates/blog/` | محذوفة |
| CSS: `.guides` · `.guide-card` · `.blog-*` · `.pagination` | `static/css/style.css` |

### مُحتفَظ به + السبب

- `.card-grid` · `.guides-grid` — **يُبقى**: `guides-grid` تستخدمها صفحة الشركات؛
  `card-grid` عامة.
- كلمة "post" العامة (مثل `post_save` signals) — غير مرتبطة بالمدونة، لم تُلمس.

### تبعيات

لا تبعيات كانت حصرية للمدونة.

### نتائج

`grep -rni "blog\|BlogPost"` على `*.py` / `*.html` = **صفر نتيجة**. `manage.py check`
نظيف. `verify.py` سطر «MENU: can access blog app» أُزيل؛ `verify_contact_policies`
ترتيب الفوتر عُدِّل لإزالة `"blog"`.

---

## 3. ملخّص تدقيق التعريب #2 (Localization / RTL Audit)

### الطريقة

سكربت Python يقارن سلاسل `{% trans %}` / `_()` (العربية) في القوالب والكود مقابل
`msgid` في `.po` المُجمَّع، + مسح Playwright لعُقد النص العربية على مسارات `/en/`،
+ فحص اتجاه القيم التقنية.

### مشاكل وُجدت وأُصلحت

| المشكلة | المصدر | الإصلاح |
|---|---|---|
| Hero eyebrow عربي على `/en/` (`نوصّل لـ 16 منطقة…`) | `core.views` `_hero_stat` نص عربي ثابت | `gettext` + `%(count)s` interpolation |
| تسميات `calculator/forms.py` + `CHOICES` في `calculator/models.py` عربية ثابتة | hardcoded | `_()` + ترجمات |
| `MenuItem.DAYS` · `Subscription.Status` · `calculator` CHOICES عربية ثابتة | hardcoded | `gettext_lazy` |
| رسائل خطأ `discount.js` عربية ثابتة | JS | نُقلت لـ `data-*` سمات في القالب |
| 52 سلسلة `{% trans %}` بلا `msgid` في الكتالوج (Session 1) | نقص | أُضيفت ~49 (الباقي كان تكراراً) |
| **eyebrow صفحة الشركات `طلب عرض سعر` عربي على `/en/`** | مفتاح صحيح ناقص من الكتالوج (كان `"اطلب عرض سعر"` و `"طلب عرض سعر شركة"` موجودين، لا `"طلب عرض سعر"`) | أُضيف `"طلب عرض سعر": "Request a Quote"` |
| رقم واتساب في الفوتر معكوس بالعربي (bidi) | span بلا `dir` | أداة مشتركة `.ltr-value { direction: ltr; unicode-bidi: isolate; }` + `dir="ltr"` على الفوتر، صفحة السياسات، كود الحاسبة |
| أسماء الموديلات وحقولها عربية فقط (تظهر عربية في admin الإنجليزي) | `verbose_name` نص عربي ثابت (ما عدا `consultations`) | لُفّت ~234 سلسلة في `gettext_lazy` عبر 8 ملفات models.py + أُضيفت 111 ترجمة إنجليزية |
| سلاسل الشريط الجانبي / لوحة القيادة في الأدمن عربية فقط | `core/unfold_conf.py` · `admin_dashboard.py` · قوالب admin | +50 ترجمة إنجليزية |
| Unfold 0.104 بلا RTL (checkbox column منفصل، شريط إجراءات مكسور، تواريخ) | القوالب تستخدم `text-left`/`pl-*`/`mr-*` ثابتة | `static/admin/css/admin-rtl.css` بنطاق `[dir="rtl"]` فقط |
| مبدّل لغة الأدمن لا يعمل (`/admin/` خارج `i18n_patterns`) | `LocaleMiddleware` يثبّته على اللغة الافتراضية | `core.middleware.AdminLocaleMiddleware` يحترم كوكي `django_language` لـ `/admin/` |
| أيقونة «محتوى الـ Hero» بالشريط الجانبي متداخلة | `icon="st-ar"` (خطأ إملائي) → Material Symbols يعرض النص الحرفي | `icon="wallpaper"` |

### قيم تقنية تبقى LTR داخل الواجهة العربية

عبر `.ltr-value` + `dir="ltr"` (الموقع) و `unicode-bidi: plaintext` (جداول الأدمن):
هاتف · إيميل · روابط · أكواد الإحالة/الدخول/الخصم · IDs · المراجع · تواريخ ISO.
**لا تُطبَّق على نص عربي عادي.**

### إصلاحات RTL/LTR بنيوية

- الاتجاه دائماً من `LANGUAGE_BIDI` — لا `text-align: right` عام.
- خصائص CSS منطقية (`margin-inline`, `inset-inline-start`, `padding-inline`).
- الشبكات ثنائية العمود تستخدم `minmax(0, Nfr)` بدل `NN%` (النسب + gap تسبّب overflow —
  أُصلح `.referral__grid`).
- الشريط الجانبي للأدمن ينعكس يميناً في RTL؛ حدّه الفاصل وأيقوناته بخصائص منطقية.

### حالة تعريب الأدمن — مكتمل

كل ما يلي مُترجم بالكامل (عربي/إنجليزي): أسماء الموديلات، تسميات الحقول،
قيم الـ choices/enums، **نصوص `help_text`** (41 نص أُضيفت)، عناوين الشريط
الجانبي وعناصره، بطاقات لوحة القيادة، breadcrumbs. `.__str__` لـ `MealType` /
`DeliveryArea` / `MenuItem` / `WeeklyMenu` / `Plan` تستخدم `.name` المُعرّبة أو
`_()` → أعمدة/قوائم FK إنجليزية في الأدمن الإنجليزي. `Plan.whatsapp_message()`
غير متأثّرة (تستخدم خاصية `.name` أصلاً).

### سلاسل بلا ترجمة إنجليزية — متعمّد + السبب

- **أسماء اللغات نفسها** (`عربي` / `العربية`) — endonyms، تبقى بلغتها الأصلية.
- **بيانات العملاء** (أسماء، أحرف أولى، أسماء الوجبات المُدخلة) — بيانات قاعدة
  بيانات، ليست سلاسل واجهة قابلة للترجمة.
- **سلاسل Unfold المدمجة** (placeholder البحث «Search apps and models») — كتالوج
  `ar` الخاص بالحزمة ناقص؛ لم نتجاوزه (نفضّل ترجمات الحزمة الأصلية).

### أرقام

`.po` = 604 msgid، 0 فارغ. `i18n_sync.main()` صار **مصدر الحقيقة**: يحدّث أي msgstr
مختلف عن القاموس ويحذف أي مفتاح غير مذكور.

### التحقّق

10 مسارات `/en/` عامة نظيفة من العربية (Playwright text-node scan). صفحات الأدمن
الإنجليزية بلا عربية في الـ chrome. جميع سويتات الـ backend + admin smoke خضراء
(262 فحص).
