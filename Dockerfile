# ---- مرحلة البناء ----
FROM python:3.12-slim AS builder

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev gettext \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ---- مرحلة التشغيل (صورة نهائية أصغر، بدون أدوات البناء) ----
FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PATH=/root/.local/bin:$PATH PYTHONPATH=/root/.local/lib/python3.12/site-packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 gettext \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home appuser

COPY --from=builder /root/.local /root/.local
COPY . .

RUN python manage.py compilemessages \
    && mkdir -p /app/media /app/staticfiles \
    && chown -R appuser:appuser /app \
    && chown -R appuser:appuser /root/.local

USER appuser

# collectstatic بيتنفذ وقت النشر (entrypoint) مو هون، عشان يقدر ياخذ متغيرات
# البيئة النهائية (مثل DATABASE_URL) الصحيحة وقت التشغيل الفعلي.
EXPOSE 8000
CMD ["sh", "-c", "python manage.py collectstatic --noinput && python manage.py migrate --noinput && gunicorn lowcalories.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 60"]
