"""
يرسل طلب تقييم للاشتراكات اللي بدأت من 7 أيام أو أكثر وما انبعتلها طلب تقييم قبل.

    python manage.py send_review_requests

يعلّم كل اشتراك بـ review_requested_at بعد الإرسال عشان ما ينبعتله ثاني مرة.
يشتغل بأمان بدون توكن واتساب حقيقي (تسجيل فقط).
"""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import Subscription
from core.console import force_utf8_stdout
from core.whatsapp_service import WhatsAppService

DAYS_AFTER_START = 7


class Command(BaseCommand):
    help = "يرسل طلبات التقييم للاشتراكات اللي مرّ على بدايتها 7 أيام+."

    def add_arguments(self, parser):
        parser.add_argument(
            "--days", type=int, default=DAYS_AFTER_START,
            help=f"عدد الأيام بعد بداية الاشتراك (افتراضي {DAYS_AFTER_START}).",
        )

    def handle(self, *args, **options):
        force_utf8_stdout()
        service = WhatsAppService()
        cutoff = timezone.localdate() - timedelta(days=options["days"])

        due = list(
            Subscription.objects.filter(
                review_requested_at__isnull=True,
                start_date__lte=cutoff,
                status__in=[Subscription.Status.ACTIVE, Subscription.Status.EXPIRED],
            ).select_related("customer")
        )

        sent = 0
        for subscription in due:
            result = service.send_review_request(subscription.customer)
            if result.get("status") in {"sent", "logged"}:
                subscription.review_requested_at = timezone.now()
                subscription.save(update_fields=["review_requested_at"])
                sent += 1

        mode = "إرسال فعلي" if service.is_configured else "تسجيل فقط (بدون توكن)"
        self.stdout.write(self.style.SUCCESS(
            f"{sent} طلب تقييم من أصل {len(due)} مؤهّل — الوضع: {mode}"
        ))
