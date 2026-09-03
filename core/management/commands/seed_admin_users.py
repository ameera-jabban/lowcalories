"""
ينشئ 3 مستخدمين تجريبيين — واحد لكل دور — لاختبار الصلاحيات فعلياً.

    python manage.py seed_admin_users

idempotent: update_or_create + إعادة ضبط كلمة السر والدور كل مرة.
يستدعي setup_roles تلقائياً أولاً حتى تكون المجموعات موجودة.

⚠️ كلمات السر هون للاختبار فقط — غيّرها أو احذف المستخدمين قبل الإنتاج.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction

from core.management.commands.setup_roles import (
    ROLE_GENERAL_MANAGER,
    ROLE_MENU_MANAGER,
    ROLE_ORDERS_STAFF,
    _force_utf8_stdout,
)

DEMO_USERS = [
    ("gm_demo", "gm@lowcalories.local", "LowCalGM2026!", ROLE_GENERAL_MANAGER),
    ("menu_demo", "menu@lowcalories.local", "LowCalMenu2026!", ROLE_MENU_MANAGER),
    ("orders_demo", "orders@lowcalories.local", "LowCalOrders2026!", ROLE_ORDERS_STAFF),
]


class Command(BaseCommand):
    help = "ينشئ 3 مستخدمين تجريبيين (واحد لكل دور) — idempotent."

    @transaction.atomic
    def handle(self, *args, **options):
        _force_utf8_stdout()
        call_command("setup_roles")

        User = get_user_model()
        for username, email, password, role_name in DEMO_USERS:
            group = Group.objects.get(name=role_name)
            user, _ = User.objects.update_or_create(
                username=username,
                defaults={"email": email, "is_staff": True, "is_superuser": False, "is_active": True},
            )
            user.set_password(password)
            user.save()
            user.groups.set([group])
            self.stdout.write(
                self.style.SUCCESS(f"  {username}  ({role_name})  password: {password}")
            )

        self.stdout.write(self.style.SUCCESS("Demo users ready."))
