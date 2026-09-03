# 🚀 دليل نشر Low Calories Jordan للإنتاج

كل الإعدادات هون **مُختبرة فعلياً** بهالبيئة (مو نظرية):
- ✅ `DEBUG=False` + تحويل HTTPS تلقائي + كل هيدرز الأمان
- ✅ `collectstatic` يشتغل صح مع WhiteNoise (ضغط + hash + cache طويل المدى)
- ✅ gunicorn يشغّل المشروع فعلياً عبر HTTP حقيقي (مو Django dev server)
- ✅ `requirements.txt` ينثبّت ببيئة نضيفة تماماً بدون أخطاء
- ⚠️ Docker build ما قدرت أختبره فعلياً (البيئة يلي بنيت فيها المشروع ما فيها Docker daemon)
  — الملفات مكتوبة بأنماط قياسية مجرّبة، بس جرّبها عندك قبل ما تعتمد عليها بالإنتاج مباشرة

اختار طريقة النشر المناسبة إلك:

---

## الطريقة 1: PaaS (Render / Railway) — الأسهل، أنصح فيها للبداية

1. ارفع المشروع لـ GitHub
2. أنشئ حساب على [Render](https://render.com) أو [Railway](https://railway.app)
3. أنشئ:
   - **Web Service** من الريبو (بيكتشف `Procfile` تلقائياً)
   - **PostgreSQL** database من نفس المنصة (بيعطيك `DATABASE_URL` جاهز)
   - (اختياري) **Redis** لو بدك أكتر من instance/worker
4. بمتغيرات البيئة (Environment Variables) بلوحة التحكم تبع المنصة، ضيف كل يلي بملف
   `.env.example` (خصوصاً `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `DATABASE_URL`)
5. Deploy. الـ `Procfile` بيشغّل migrate + collectstatic تلقائياً قبل ما يشغّل gunicorn.

**ملاحظة مهمة عن الصور**: هالمنصات غالباً ملف نظامها مؤقت (ephemeral) — أي صورة
يرفعها الأدمن (لوجو، صور منيو) رح تضيع عند أي إعادة نشر جديدة. الحل: استخدم
`django-storages` + S3/Cloudflare R2 لتخزين الوسائط. قلي إذا بدك هالإضافة.

---

## الطريقة 2: VPS تقليدي (DigitalOcean, Linode, أي سيرفر أوبنتو)

```bash
# 1. على السيرفر
sudo apt update && sudo apt install python3-venv python3-pip postgresql nginx certbot python3-certbot-nginx gettext

# 2. جهّز قاعدة البيانات
sudo -u postgres createdb lowcalories
sudo -u postgres createuser lowcalories -P   # بيسألك باسورد

# 3. انسخ المشروع لـ /var/www/lowcalories وجهّز البيئة
cd /var/www/lowcalories
python3 -m venv venv
venv/bin/pip install -r requirements.txt
cp .env.example .env
nano .env   # عبّي القيم الحقيقية (SECRET_KEY, DATABASE_URL, ALLOWED_HOSTS...)

venv/bin/python manage.py migrate
venv/bin/python manage.py setup_roles
venv/bin/python scripts/i18n_sync.py            # يجمّع django.mo (بديل compilemessages — البيئة بلا GNU gettext)
venv/bin/python manage.py collectstatic --noinput
venv/bin/python manage.py createsuperuser

# 4. فعّل systemd service (الملف موجود بـ deploy/lowcalories.service)
sudo mkdir -p /run/lowcalories
sudo cp deploy/lowcalories.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now lowcalories

# 5. فعّل nginx (الملف موجود بـ deploy/nginx.conf)
sudo cp deploy/nginx.conf /etc/nginx/sites-available/lowcalories
sudo ln -s /etc/nginx/sites-available/lowcalories /etc/nginx/sites-enabled/
sudo certbot --nginx -d lowcaloriesjordan.com -d www.lowcaloriesjordan.com  # شهادة SSL مجانية
sudo systemctl restart nginx
```

---

## الطريقة 3: Docker

```bash
cp .env.example .env
nano .env   # عبّي DJANGO_SECRET_KEY و DJANGO_ALLOWED_HOSTS على الأقل

docker compose up -d --build
docker compose exec web python manage.py createsuperuser
```

هذا بيشغّل 3 حاويات: `web` (Django+gunicorn)، `db` (PostgreSQL)، `redis` (Cache).
النشر الفعلي (migrate + collectstatic) صاير تلقائياً بأول تشغيل عبر الـ `CMD` بالـ Dockerfile.

**⚠️ كرر: هاي الطريقة ما اختبرتها فعلياً هون** (بيئتي ما فيها Docker) — الملفات
مبنية صح نظرياً بس جرّبها محلياً `docker compose up` قبل الاعتماد عليها بالإنتاج.

---

## ✅ Checklist نهائي قبل الإطلاق الفعلي

- [ ] `DJANGO_SECRET_KEY` جديد وعشوائي (مو نفس القيمة الافتراضية بالكود)
- [ ] `DJANGO_DEBUG=False`
- [ ] `DJANGO_ALLOWED_HOSTS` بالدومين الحقيقي بالضبط
- [ ] `DATABASE_URL` يشاور PostgreSQL حقيقي (مو SQLite)
- [ ] شهادة SSL شغالة (Let's Encrypt مجانية عبر certbot)
- [ ] رقم الواتساب الحقيقي محدّث من لوحة التحكم
- [ ] الأسعار/الخطط/مناطق التوصيل محدّثة بالبيانات الحقيقية
- [ ] `python manage.py createsuperuser` بباسورد قوي (مو `LowCal2026!` تبع التجربة)
- [ ] Backup تلقائي لقاعدة البيانات (معظم مزودي PostgreSQL المُدار بيوفروها تلقائياً)
- [ ] `/healthz/` مربوط بمراقبة خارجية (UptimeRobot مجاني مثلاً) لتنبيهك لو الموقع وقع
