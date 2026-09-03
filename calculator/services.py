"""
منطق حساب السعرات والماكروز — نفس معادلة Mifflin-St Jeor المستخدمة بموقع mightygainz.com
كل الحساب صايره بالسيرفر (Python)، مو بس JavaScript — عشان يكون دقيق، آمن،
وقابل نخزنه بقاعدة البيانات ونحلله لاحقاً.
"""

ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
    "athlete": 2.0,
}

GOAL_ADJUSTMENT = {
    "loss": -500,
    "maintain": 0,
    "gain": 300,
}

MIN_SAFE_CALORIES = {"male": 1500, "female": 1200}


def calculate_bmr(gender: str, weight_kg: float, height_cm: float, age: int) -> float:
    """معادلة Mifflin-St Jeor لحساب معدل الأيض الأساسي (BMR)"""
    base = 10 * weight_kg + 6.25 * height_cm - 5 * age
    return base + 5 if gender == "male" else base - 161


def calculate_result(gender, weight_kg, height_cm, age, activity_level, goal):
    """
    يرجّع dict فيه السعرات اليومية وتوزيع الماكروز.
    """
    bmr = calculate_bmr(gender, weight_kg, height_cm, age)
    tdee = bmr * ACTIVITY_MULTIPLIERS[activity_level]
    target_calories = tdee + GOAL_ADJUSTMENT[goal]

    # حد أدنى آمن
    min_safe = MIN_SAFE_CALORIES[gender]
    target_calories = max(target_calories, min_safe)
    target_calories = round(target_calories)

    # توزيع ماكروز تقريبي: بروتين 30% / كارب 40% / دهون 30% (بروتين وكارب = 4 سعرة/غرام، دهون = 9)
    protein_g = round((target_calories * 0.30) / 4)
    carbs_g = round((target_calories * 0.40) / 4)
    fat_g = round((target_calories * 0.30) / 9)

    # نِسَب المساهمة بالسعرات لكل ماكرو — يستخدمها القالب لرسم "الدونات" البصري
    protein_cal = protein_g * 4
    carbs_cal = carbs_g * 4
    fat_cal = fat_g * 9
    macro_total = protein_cal + carbs_cal + fat_cal or 1

    return {
        "calories": target_calories,
        "protein_g": protein_g,
        "carbs_g": carbs_g,
        "fat_g": fat_g,
        "protein_pct": round(protein_cal * 100 / macro_total),
        "carbs_pct": round(carbs_cal * 100 / macro_total),
        "fat_pct": round(fat_cal * 100 / macro_total),
    }


def suggest_plan(target_calories: int, goal: str):
    """
    يقترح أقرب خطة اشتراك مناسبة بناءً على نتيجة الحاسبة.
    منطق بسيط: لسه ما في عندنا ربط سعرات↔خطة دقيق، فمؤقتاً نرجع الخطة الأكثر شعبية
    المطابقة للهدف. لاحقاً ممكن تتوسع فيها (مثلاً: خطط وجبتين للي بدهم بناء عضل).
    """
    from plans.models import Plan

    qs = Plan.objects.all()
    if goal == "gain":
        qs = qs.filter(meals_per_day__gte=2) or qs
    plan = qs.filter(is_popular=True).first() or qs.first()
    return plan
