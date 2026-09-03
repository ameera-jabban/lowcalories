"""
برنامج الإحالة: عميل يشارك كود/رابط مع صاحبه. الصاحب يشترك لأول مرة →
الاثنين ياخدوا يوم مجاني (يضيفه الأدمن يدوياً، أو تلقائياً لو تطبيق accounts
موجود — شوف Referral.mark_redeemed).
"""
import secrets

from django.db import models
from django.utils.text import slugify


def _make_code(name: str) -> str:
    """
    كود إحالة لاتيني دايماً (حروف/أرقام إنجليزية فقط) — أول 4 أحرف لاتينية من
    الاسم + 4 أرقام عشوائية. لو الاسم مش لاتيني (عربي مثلاً) نرجع للبادئة LC.
    هيك الكود ما بيخلط عربي/إنجليزي وبيظهر LTR بأي لغة.
    """
    prefix = slugify(name, allow_unicode=False)[:4].upper() or "LC"
    return f"{prefix}{secrets.randbelow(9000) + 1000}"


class ReferralCode(models.Model):
    referrer_name = models.CharField("اسم صاحب الكود", max_length=120)
    referrer_phone = models.CharField("رقم هاتفه", max_length=20, unique=True)
    code = models.SlugField("الكود", max_length=24, unique=True, allow_unicode=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "كود إحالة"
        verbose_name_plural = "أكواد الإحالة"

    def __str__(self):
        return f"{self.code} — {self.referrer_name}"

    def save(self, *args, **kwargs):
        if not self.code:
            candidate = _make_code(self.referrer_name)
            while ReferralCode.objects.filter(code=candidate).exists():
                candidate = _make_code(self.referrer_name)
            self.code = candidate
        super().save(*args, **kwargs)

    def share_path(self) -> str:
        return f"/r/{self.code}/"

    @property
    def redeemed_count(self) -> int:
        return self.referrals.filter(status=Referral.Status.REDEEMED).count()


class Referral(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "بانتظار"
        REDEEMED = "redeemed", "تم الاستبدال"
        EXPIRED = "expired", "منتهي"

    referral_code = models.ForeignKey(
        ReferralCode, on_delete=models.CASCADE, related_name="referrals", verbose_name="كود الإحالة"
    )
    referred_name = models.CharField("اسم الصديق", max_length=120)
    referred_phone = models.CharField("رقم هاتف الصديق", max_length=20)
    status = models.CharField("الحالة", max_length=12, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    redeemed_at = models.DateTimeField("تاريخ الاستبدال", null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "إحالة"
        verbose_name_plural = "الإحالات"

    def __str__(self):
        return f"{self.referred_name} ← {self.referral_code.referrer_name}"

    def mark_redeemed(self):
        """
        يعلّم الإحالة كمستبدلة + (لو تطبيق accounts موجود) يمدّد اشتراك كل من
        صاحب الكود والصديق يوم واحد — لو عند أي طرف اشتراك فعّال. لو ما في،
        يتخطّاه بصمت بدون خطأ. يرجّع رسالة توضّح شو صار.
        """
        from django.utils import timezone

        self.status = self.Status.REDEEMED
        self.redeemed_at = timezone.now()
        self.save(update_fields=["status", "redeemed_at"])

        extended = self._grant_free_days()
        if extended:
            return "تم الاستبدال + مُدّد اشتراك: " + "، ".join(extended)
        return (
            "تم الاستبدال. تذكير: أضف يوم مجاني يدوياً لـ "
            f"{self.referral_code.referrer_phone} و {self.referred_phone} "
            "(ما في اشتراك فعّال لأي طرف حالياً)."
        )

    def _grant_free_days(self):
        try:
            from datetime import timedelta

            from accounts.models import Subscription
        except Exception:
            return []

        extended = []
        phones = {
            "صاحب الكود": self.referral_code.referrer_phone,
            "الصديق": self.referred_phone,
        }
        for label, phone in phones.items():
            sub = (
                Subscription.objects.filter(
                    customer__phone_number=phone, status=Subscription.Status.ACTIVE
                )
                .order_by("-end_date")
                .first()
            )
            if sub and sub.end_date:
                sub.end_date = sub.end_date + timedelta(days=1)
                sub.save(update_fields=["end_date"])
                extended.append(f"{label} ({phone})")
        return extended
