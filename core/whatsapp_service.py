"""
طبقة تجريد فوق WhatsApp Business Cloud API الرسمي من Meta.

لماذا الـ Cloud API الرسمي وليس مكتبات غير رسمية (pywhatkit، محاكاة واتساب ويب)؟
لأن غير الرسمية تنكسر باستمرار وتخالف شروط استخدام واتساب وتعرّض الرقم للحظر.

سلوك مهم — التشغيل بدون حساب Meta Business:
    إذا كانت متغيرات البيئة WHATSAPP_CLOUD_API_TOKEN / WHATSAPP_PHONE_NUMBER_ID
    فاضية، كل ميثود هون **يسجّل الرسالة في الـ logs فقط ولا يعمل أي طلب شبكة**.
    هذا مقصود: يخلي الموقع يشتغل محلياً وعلى بيئة الاختبار بدون أي إعداد،
    ويخلي الأتمتة قابلة للاختبار (بتشوف "would send to X" في الـ logs).

أي فشل اتصال (timeout، رد غير متوقع من الـ API) يُلتقط ويُسجَّل، وما يكسر
الصفحة/الأمر اللي نادى الخدمة.

للتفعيل بالإنتاج: شوف قسم "WhatsApp Automation" في README.md.
"""
from __future__ import annotations

import logging

import requests
from django.conf import settings
from django.urls import reverse

logger = logging.getLogger(__name__)

_TIMEOUT_SECONDS = 10


class WhatsAppService:
    """واجهة موحّدة لإرسال رسائل واتساب المعاملاتية (transactional)."""

    def __init__(self):
        self.token = settings.WHATSAPP_CLOUD_API_TOKEN
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.api_version = settings.WHATSAPP_CLOUD_API_VERSION

    # ------------------------------------------------------------------ #
    # الأساس
    # ------------------------------------------------------------------ #
    @property
    def is_configured(self) -> bool:
        return bool(self.token and self.phone_number_id)

    def _endpoint(self) -> str:
        return f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}/messages"

    def _send_text(self, to_phone: str, body: str) -> dict:
        """
        يرسل رسالة نصية بسيطة. يرجّع dict فيه نتيجة العملية (ما يرمي استثناء
        للأعلى إطلاقاً — المنادي ما لازم ينكسر لو واتساب فشل).
        """
        to_phone = (to_phone or "").strip().lstrip("+")
        if not to_phone:
            logger.warning("WhatsApp: تم تجاهل رسالة بدون رقم هاتف")
            return {"status": "skipped", "reason": "no_phone"}

        if not self.is_configured:
            # الحالة الطبيعية محلياً / بيئة الاختبار
            logger.info("WhatsApp not configured — would send to %s: %s", to_phone, body)
            return {"status": "logged", "to": to_phone, "body": body}

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_phone,
            "type": "text",
            "text": {"preview_url": True, "body": body},
        }
        headers = {"Authorization": f"Bearer {self.token}"}

        try:
            resp = requests.post(
                self._endpoint(), json=payload, headers=headers, timeout=_TIMEOUT_SECONDS
            )
            resp.raise_for_status()
            data = resp.json()
            logger.info("WhatsApp sent to %s (id=%s)", to_phone, data.get("messages", [{}])[0].get("id"))
            return {"status": "sent", "response": data}
        except requests.RequestException as exc:
            logger.error("WhatsApp send to %s failed: %s", to_phone, exc)
            return {"status": "error", "error": str(exc)}
        except ValueError as exc:  # رد مش JSON
            logger.error("WhatsApp unexpected (non-JSON) response for %s: %s", to_phone, exc)
            return {"status": "error", "error": "invalid_response"}

    @staticmethod
    def _abs_url(path: str) -> str:
        return f"{settings.SITE_BASE_URL.rstrip('/')}{path}"

    # ------------------------------------------------------------------ #
    # الرسائل الجاهزة
    # ------------------------------------------------------------------ #
    def send_order_confirmation(self, customer, plan) -> dict:
        """تأكيد استلام طلب اشتراك جديد."""
        plan_line = (
            f"{plan.days} يوم - {plan.meal_type.name_ar} - {plan.meals_per_day} وجبة "
            f"({plan.price_jod} د.أ)"
            if plan
            else "اشتراك"
        )
        body = (
            f"أهلاً {customer.name} 👋\n"
            f"استلمنا طلب اشتراكك في Low Calories Jordan:\n"
            f"• {plan_line}\n\n"
            f"رح نتواصل معك لتأكيد التفاصيل وموعد أول توصيلة. شكراً لثقتك 🧡"
        )
        return self._send_text(customer.phone_number, body)

    def send_weekly_menu_reminder(self, customer) -> dict:
        """تذكير بنزول منيو الأسبوع الجديد."""
        menu_url = self._abs_url(reverse("menu:menu_list"))
        body = (
            f"مرحبا {customer.name} 🍽️\n"
            f"نزل منيو هذا الأسبوع! شوف وجباتك من هون:\n{menu_url}\n\n"
            f"بالعافية عليك 💪"
        )
        return self._send_text(customer.phone_number, body)

    def send_review_request(self, customer) -> dict:
        """
        طلب تقييم بعد فترة من بداية الاشتراك. الرابط يودّي لفورم قصير
        بيضيف Testimonial تلقائياً (فبيصير نظام التقييمات اليدوي شبه مؤتمت).
        """
        review_url = self._abs_url(
            reverse("accounts:leave_review", kwargs={"access_code": customer.access_code})
        )
        body = (
            f"مرحبا {customer.name} 🌟\n"
            f"صار لك فترة معنا — كيف كانت تجربتك؟\n"
            f"قيّمنا بدقيقة من هون:\n{review_url}\n\n"
            f"رأيك بيفرق معنا كتير 🙏"
        )
        return self._send_text(customer.phone_number, body)
