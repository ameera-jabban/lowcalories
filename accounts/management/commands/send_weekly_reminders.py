"""
يرسل تذكير "نزل منيو الأسبوع الجديد" لكل عميل عنده اشتراك فعّال.

    python manage.py send_weekly_reminders

يشتغل يدوياً الآن، ويمكن جدولته لاحقاً عبر cron (مثلاً كل يوم أحد صباحاً).
يشتغل بأمان بدون توكن واتساب حقيقي — الخدمة تسجّل "would send to X" فقط.
"""
from django.core.management.base import BaseCommand

from accounts.models import Customer, Subscription
from core.console import force_utf8_stdout
from core.whatsapp_service import WhatsAppService


class Command(BaseCommand):
    help = "يرسل تذكير المنيو الأسبوعي لأصحاب الاشتراكات الفعّالة."

    def handle(self, *args, **options):
        force_utf8_stdout()
        service = WhatsAppService()
        customers = Customer.objects.filter(
            subscriptions__status=Subscription.Status.ACTIVE
        ).distinct()

        sent = 0
        for customer in customers:
            result = service.send_weekly_menu_reminder(customer)
            if result.get("status") in {"sent", "logged"}:
                sent += 1

        mode = "إرسال فعلي" if service.is_configured else "تسجيل فقط (بدون توكن)"
        self.stdout.write(self.style.SUCCESS(
            f"تمت معالجة {customers.count()} عميل ({sent} تذكير) — الوضع: {mode}"
        ))
