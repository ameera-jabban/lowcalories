from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"
    verbose_name = "بوابة العملاء"

    def ready(self):
        # يربط إشارة post_save على Subscription (تأكيد الطلب التلقائي عبر واتساب)
        from . import signals  # noqa: F401
