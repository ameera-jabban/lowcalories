"""
عند إنشاء اشتراك جديد (عادةً من لوحة التحكم بعد تأكيد الطلب يدوياً على واتساب)،
نبعت رسالة تأكيد تلقائية للعميل عبر WhatsApp Business Cloud API.

اخترنا signal (مش تعديل save) عشان:
- ما نخلط منطق "الإشعارات" مع منطق حفظ الموديل
- نضمن الإرسال مرة وحدة فقط عند الإنشاء (created=True)
- لو فشل واتساب، ما يأثر على حفظ الاشتراك بلوحة التحكم (كله داخل try/except،
  والخدمة نفسها ما ترمي استثناءات)
"""
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from core.whatsapp_service import WhatsAppService
from .models import Subscription

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Subscription, dispatch_uid="accounts_subscription_confirmation")
def send_confirmation_on_new_subscription(sender, instance: Subscription, created, **kwargs):
    if not created:
        return
    try:
        WhatsAppService().send_order_confirmation(instance.customer, instance.plan)
    except Exception:  # noqa: BLE001 — الإشعار ما لازم يكسر حفظ الاشتراك أبداً
        logger.exception("فشل إرسال تأكيد الاشتراك للعميل %s", instance.customer_id)
