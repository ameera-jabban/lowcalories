"""
ينشئ (أو يحدّث) أدوار لوحة التحكم الثلاثة كـ Django Groups بصلاحياتهم.

    python manage.py setup_roles

idempotent بالكامل — تقدر تشغّله أكثر من مرة بدون تكرار أو فشل: يستخدم
get_or_create للمجموعة و set() للصلاحيات (تستبدل القائمة كاملة كل مرة).
"""
import sys

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from django.db import transaction


def _force_utf8_stdout():
    """كونسول Windows الافتراضي (cp1252) ما يطبع عربي — نجبره UTF-8."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

# أسماء الأدوار — تُستخدم كمرجع بباقي الكود وبالـ README
ROLE_GENERAL_MANAGER = "مدير عام"
ROLE_MENU_MANAGER = "مسؤول منيو"
ROLE_ORDERS_STAFF = "موظف متابعة طلبات"

# تطبيقات ما حدا (غير المدير العام) يتحكم فيها من الأدوار الجاهزة
_INFRA_APPS = {"contenttypes", "sessions"}


class Command(BaseCommand):
    help = "ينشئ أدوار لوحة التحكم (Groups) بصلاحياتها — idempotent."

    @transaction.atomic
    def handle(self, *args, **options):
        _force_utf8_stdout()
        all_perms = Permission.objects.select_related("content_type")

        # ---- 1) مدير عام: كل شي ما عدا إدارة المستخدمين/المجموعات (auth) ----
        gm_perms = all_perms.exclude(
            content_type__app_label__in=_INFRA_APPS | {"auth"}
        )

        # ---- 2) مسؤول منيو: CRUD كامل على menu فقط ----
        menu_perms = all_perms.filter(content_type__app_label="menu")

        # ---- 3) موظف متابعة طلبات: view فقط على Lead + CalorieCalculation ----
        orders_perms = all_perms.filter(
            content_type__app_label="leads", codename="view_lead"
        ) | all_perms.filter(
            content_type__app_label="calculator", codename="view_caloriecalculation"
        )

        roles = {
            ROLE_GENERAL_MANAGER: gm_perms,
            ROLE_MENU_MANAGER: menu_perms,
            ROLE_ORDERS_STAFF: orders_perms,
        }

        for name, perms_qs in roles.items():
            group, created = Group.objects.get_or_create(name=name)
            group.permissions.set(list(perms_qs))
            verb = "created" if created else "updated"
            self.stdout.write(
                self.style.SUCCESS(f"  [{verb}] {name} -> {group.permissions.count()} permissions")
            )

        self.stdout.write(self.style.SUCCESS("Roles ready: setup_roles finished."))
