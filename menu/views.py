from django.shortcuts import render
from django.utils.translation import gettext as _

from .models import MenuItem, WeeklyMenu


def _meal_card(item):
    """بطاقة .mcard موحّدة لوجبة منيو — نفس تصميم بطاقات الوجبات بباقي الموقع."""
    from core.homepage import _card_image

    legend = []
    if item.protein_g:
        legend.append({"key": "protein", "label": _("بروتين"), "value": _("%(g)sغ") % {"g": item.protein_g}})
    if item.carbs_g:
        legend.append({"key": "carbs", "label": _("كارب"), "value": _("%(g)sغ") % {"g": item.carbs_g}})
    if item.fat_g:
        legend.append({"key": "fat", "label": _("دهون"), "value": _("%(g)sغ") % {"g": item.fat_g}})
    return {
        "variant": "meal", "layout": "stacked",
        "image": _card_image(item.image),
        "image_alt": item.name,
        "badge": _("%(c)s سعرة") % {"c": item.calories} if item.calories else None,
        "category": item.meal_type.name if item.meal_type else "",
        "title": item.name,
        "macro_legend": legend,
    }


def menu_list(request):
    """
    المنيو الأسبوعي الفعّال، مرتّب حسب اليوم. ديناميكي بالكامل — أي تعديل
    بلوحة التحكم بينعكس فوراً. أول يوم فيه وجبات يكون مفعّل افتراضياً.
    """
    weekly_menu = WeeklyMenu.get_current()
    days = []
    if weekly_menu:
        buckets = {}
        for item in weekly_menu.items.select_related("meal_type").all():
            buckets.setdefault(item.day_of_week, []).append(item)
        for value, label in MenuItem.DAYS:
            if value in buckets:
                days.append({
                    "value": value,
                    "label": label,
                    "cards": [_meal_card(i) for i in buckets[value]],
                })

    return render(request, "menu/menu_list.html", {
        "weekly_menu": weekly_menu,
        "days": days,
    })
