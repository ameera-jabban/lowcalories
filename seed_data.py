"""
بيانات Placeholder لتشغيل الموقع فوراً — شغّلها بالأمر:
    python manage.py shell < seed_data.py

⚠️ كل رقم/سعر هون تقديري لأجل ما يطلع الموقع فاضي. لازم تستبدلها بالحقيقي
   قبل ما تنشر (شوف ملف TODO_قبل_الإطلاق.md).
"""
import datetime

from consultations.models import ConsultationRequest
from core.models import FAQ, HeroGoal, HowItWorksStep, SiteFeature, SiteSettings, Testimonial
from menu.models import MealType, WeeklyMenu, MenuItem
from plans.models import DiscountCode, Plan, DeliveryArea

# ---- إعدادات الموقع ----
SiteSettings.objects.update_or_create(
    id=1,
    defaults=dict(
        brand_name_ar="Low Calories Jordan | لو كالوريز",
        brand_name_en="Low Calories Jordan",
        whatsapp_number="+962 79 123 4567",  # 🔴 TODO: رقم واتساب الحقيقي (يُنظَّف آلياً)
        whatsapp_display="+962 79 123 4567",  # 🔴 TODO: نفس الرقم بصيغة العرض
        whatsapp_default_message_ar="مرحبا Low Calories Jordan، حابب أستفسر عن الخطط 🙌",
        whatsapp_default_message_en="Hi Low Calories Jordan, I'd like to ask about your plans 🙌",
        instagram_url="https://www.instagram.com/lowcalories_jor/",
        instagram_username="lowcalories_jor",
        location_ar="عمّان، الأردن",
        location_en="Amman, Jordan",
        support_email="",  # 🔴 TODO: بريد الدعم الرسمي
        google_rating=5.0,
        reviews_count=0,
        facebook_pixel_id="",  # 🔴 TODO: حط رقم الـ Pixel هون لما يصير عندك حساب Meta Business
        consultation_price_jod=15,  # 🔴 TODO: سعر جلسة الاستشارة الحقيقي
        consultation_duration_min=20,
        primary_color="#FD7B01",
        secondary_color="#00A850",
        soft_bg_color="#FFF3E6",
        working_hours_ar="يومياً ٩ ص – ٩ م",
        working_hours_en="Daily 9 AM – 9 PM",
    ),
)

# ---- مزايا "ليش تختارنا" (الصفحة الرئيسية) ----
features_data = [
    ("calories", "سعرات محسوبة بدقة", "Precisely calculated calories",
     "كل وجبة معروف سعراتها وماكروزها بالضبط.", "Every meal's calories and macros are known exactly.", 1),
    ("delivery", "توصيل يومي", "Daily delivery",
     "وجباتك توصلك طازة لباب بيتك كل يوم داخل عمّان.", "Fresh meals to your door every day across Amman.", 2),
    ("variety", "منيو متنوّع", "Varied menu",
     "منيو جديد كل أسبوع — دجاج، لحم، سمك، زيرو كارب.", "A new menu every week — chicken, beef, fish, zero-carb.", 3),
    ("support", "متابعة ودعم", "Guidance & support",
     "فريقنا معك على واتساب لأي سؤال أو تعديل.", "Our team is on WhatsApp for any question or change.", 4),
]
for icon, t_ar, t_en, d_ar, d_en, order in features_data:
    SiteFeature.objects.update_or_create(
        title_ar=t_ar,
        defaults=dict(icon=icon, title_ar=t_ar, title_en=t_en, text_ar=d_ar, text_en=d_en,
                      order=order, is_active=True),
    )

# ---- تقييمات تجريبية (تظهر تلقائياً لحد ما تربط خدمة تقييمات خارجية حقيقية) ----
sample_testimonials = [
    ("أحمد", 5, "أكل طازة وطعمه زاكي، والتوصيل دايماً بالوقت.", "Fresh food, great taste, always on time delivery."),
    ("سارة", 5, "خسرت وزن وأنا مرتاحة، ما في حرمان.", "Lost weight comfortably, no starving myself."),
    ("محمد", 4, "المنيو متنوع وما بزهق، بس بحب لو في خيارات نباتية أكتر.", "Varied menu, wish there were more vegetarian options."),
    ("لينا", 5, "الحاسبة ساعدتني أعرف احتياجي بالظبط، وخطتي مفصّلة عليّ.", "The calculator helped me know exactly what I need — my plan fits me."),
    ("خالد", 5, "بنيت عضل وأنا ملتزم بالسعرات بدون ما أطبخ.", "Gained muscle while hitting my calories without cooking."),
    ("رنا", 4, "خدمة الواتساب سريعة وسهّلت عليّ تغيير الخطة.", "WhatsApp support is fast and made changing my plan easy."),
]
for name, rating, text_ar, text_en in sample_testimonials:
    Testimonial.objects.update_or_create(
        customer_name=name,
        defaults=dict(customer_name=name, rating=rating, text_ar=text_ar, text_en=text_en, is_published=True),
    )

# ---- أنواع الوجبات (مع توزيع ماكروز تقريبي — يظهر على كروت الخطط) ----
meal_types_data = [
    dict(name_ar="دجاج", name_en="Chicken", slug="chicken", icon_emoji="🍗",
         typical_protein_pct=45, typical_carbs_pct=35, typical_fat_pct=20),
    dict(name_ar="لحم", name_en="Beef", slug="beef", icon_emoji="🥩",
         typical_protein_pct=40, typical_carbs_pct=33, typical_fat_pct=27),
    dict(name_ar="سمك", name_en="Fish", slug="fish", icon_emoji="🐟",
         typical_protein_pct=42, typical_carbs_pct=38, typical_fat_pct=20),
    dict(name_ar="زيرو كارب", name_en="Zero Carb", slug="zero-carb", icon_emoji="🥗",
         typical_protein_pct=55, typical_carbs_pct=10, typical_fat_pct=35),
    dict(name_ar="مشكل", name_en="Mixed", slug="mixed", icon_emoji="🍽️",
         typical_protein_pct=40, typical_carbs_pct=40, typical_fat_pct=20),
]
meal_types = {}
for mt in meal_types_data:
    obj, _ = MealType.objects.update_or_create(slug=mt["slug"], defaults=mt)
    meal_types[mt["slug"]] = obj

chicken, beef, fish, zero_carb, mixed = (
    meal_types["chicken"], meal_types["beef"], meal_types["fish"],
    meal_types["zero-carb"], meal_types["mixed"],
)

# ---- خطط تقديرية (🔴 عدّل الأسعار/الأيام حسب الحقيقة) ----
plans_data = [
    dict(days=20, meal_type=chicken, meals_per_day=1, price_jod=85, is_popular=True),
    dict(days=20, meal_type=mixed, meals_per_day=1, price_jod=95, is_popular=False),
    dict(days=20, meal_type=chicken, meals_per_day=2, price_jod=155, is_popular=False),
    dict(days=20, meal_type=mixed, meals_per_day=2, price_jod=165, is_popular=True),
    dict(days=24, meal_type=chicken, meals_per_day=1, price_jod=102, is_popular=False),
    dict(days=26, meal_type=chicken, meals_per_day=1, price_jod=110, is_popular=False),
]
for p in plans_data:
    Plan.objects.update_or_create(
        days=p["days"], meal_type=p["meal_type"], meals_per_day=p["meals_per_day"],
        defaults=p,
    )

# ---- مناطق التوصيل ----
areas = [
    ("وسط البلد", "Downtown"), ("جبل عمان", "Jabal Amman"), ("الشميساني", "Shmeisani"),
    ("عبدون", "Abdoun"), ("الصويفية", "Sweifieh"), ("خلدا", "Khalda"),
    ("الجبيهة", "Jubaiha"), ("تلاع العلي", "Tla' Al-Ali"), ("دير غبار", "Deir Ghbar"),
    ("أم السماق", "Um Al-Summaq"), ("مرج الحمام", "Marj Al-Hamam"), ("صويلح", "Sweileh"),
    ("الرابية", "Al-Rabiah"), ("العبدلي", "Abdali"), ("الدوار السابع", "7th Circle"),
    ("الدوار الثامن", "8th Circle"),
]
for name_ar, name_en in areas:
    DeliveryArea.objects.update_or_create(
        name_ar=name_ar, defaults=dict(name_ar=name_ar, name_en=name_en, is_active=True)
    )

# ---- منيو أسبوعي تجريبي ----
today = datetime.date.today()
sunday = today - datetime.timedelta(days=(today.weekday() + 1) % 7)
weekly_menu, _ = WeeklyMenu.objects.update_or_create(
    week_start_date=sunday, defaults=dict(week_start_date=sunday, is_active=True)
)
weekly_menu.items.all().delete()

sample_meals = [
    (0, chicken, "دجاج مشوي مع أرز بسمتي وخضار", "Grilled Chicken with Basmati Rice & Veggies", 480, 40, 45, 12),
    (0, zero_carb, "دجاج مشوي مع خضار سوتيه", "Grilled Chicken with Sautéed Veggies", 350, 42, 10, 14),
    (1, beef, "لحم مفروم مع بطاطا مهروسة", "Ground Beef with Mashed Potatoes", 520, 38, 40, 18),
    (1, fish, "سمك مشوي مع أرز أسمر", "Grilled Fish with Brown Rice", 420, 36, 42, 10),
    (2, chicken, "دجاج كاري مع أرز", "Chicken Curry with Rice", 460, 39, 44, 13),
    (3, beef, "ستيك لحم مع خضار مشوية", "Beef Steak with Grilled Vegetables", 500, 41, 30, 20),
    (4, fish, "سلمون مشوي مع كينوا", "Grilled Salmon with Quinoa", 470, 37, 38, 16),
]
for day, mt, name_ar, name_en, cal, p, c, f in sample_meals:
    MenuItem.objects.create(
        weekly_menu=weekly_menu, meal_type=mt, day_of_week=day,
        name_ar=name_ar, name_en=name_en, calories=cal, protein_g=p, carbs_g=c, fat_g=f,
    )

# ---- طلب استشارة تجريبي (يظهر بلوحة التحكم) ----
ConsultationRequest.objects.get_or_create(
    full_name="سارة أحمد",
    phone="962791112233",
    defaults=dict(
        email="",
        preferred_contact=ConsultationRequest.ContactMethod.WHATSAPP,
        goal="خسارة وزن وخطة وجبات",
        notes="بشتغل دوام طويل وبحب أكل بسيط وسريع.",
        language="ar",
        source="consultations_page",
    ),
)

# ---- كود خصم تجريبي لأول اشتراك ----
DiscountCode.objects.update_or_create(
    code="WELCOME15",
    defaults=dict(code="WELCOME15", discount_percent=15, is_active=True, max_uses=100),
)

# ---- أهداف الـ Hero المتغيّرة ----
hero_goals_data = [
    ("خسارة وزن", "To Lose Weight", 1),
    ("بناء عضل", "To Gain Muscle", 2),
    ("أكل صحي بدون تعقيد", "Healthy Eating, Simplified", 3),
    ("تثبيت وزنك", "To Maintain Your Weight", 4),
]
for t_ar, t_en, order in hero_goals_data:
    HeroGoal.objects.update_or_create(text_ar=t_ar, defaults=dict(text_ar=t_ar, text_en=t_en, order=order, is_active=True))

# ---- خطوات "كيف يعمل" ----
steps_data = [
    ("احسب احتياجك", "Find your plan", "استخدم الحاسبة لتعرف سعراتك وهدفك.", "Use the calculator to know your calories and goal.", 1),
    ("اختر خطتك", "You choose, we cook", "اختر عدد الأيام ونوع الوجبات اللي بناسبك.", "Pick your days and meal type.", 2),
    ("توصلك يومياً", "Daily delivery", "وجباتك طازة لباب بيتك كل يوم داخل عمّان.", "Fresh meals to your door every day in Amman.", 3),
]
for t_ar, t_en, d_ar, d_en, order in steps_data:
    HowItWorksStep.objects.update_or_create(title_ar=t_ar, defaults=dict(
        title_ar=t_ar, title_en=t_en, text_ar=d_ar, text_en=d_en, order=order, is_active=True))

# ---- أسئلة شائعة ----
faq_data = [
    ("كيف أشترك؟", "How do I subscribe?",
     "اختر خطتك من صفحة الخطط واضغط «اشترك الآن» — بنحوّلك على واتساب برسالة جاهزة، والفريق بيأكد معك التفاصيل والدفع.",
     "Pick a plan and tap “Subscribe Now” — we take you to WhatsApp with a ready message, and the team confirms details and payment with you.", 1),
    ("هل أقدر أغيّر نوع الوجبات بعد الاشتراك؟", "Can I change my meal type after subscribing?",
     "أكيد. راسلنا على واتساب أو من بوابة «اشتراكي» واطلب التغيير، وبنطبّقه من عندنا.",
     "Yes. Message us on WhatsApp or use the “My Subscription” portal to request a change and we apply it.", 2),
    ("هل أقدر أجمّد اشتراكي؟", "Can I pause my subscription?",
     "نعم، تقدر تجمّد اشتراكك مؤقتاً وتستأنفه لاحقاً — الأيام المجمّدة تنضاف على تاريخ الانتهاء.",
     "Yes, you can freeze temporarily and resume later — frozen days are added to your end date.", 3),
    ("متى يوصل الطلب؟", "When is delivery?",
     "التوصيل يومي داخل عمّان بمواعيد ثابتة نتفق عليها معك عند الاشتراك.",
     "Delivery is daily across Amman at a fixed time agreed at subscription.", 4),
    ("هل في حد أدنى للاشتراك؟", "Is there a minimum subscription?",
     "أقصر خطة عندنا ٢٠ يوم. تقدر تسأل الفريق عن خيارات أقصر لو بدك تجرّب.",
     "Our shortest plan is 20 days. Ask the team about shorter trial options.", 5),
]
for q_ar, q_en, a_ar, a_en, order in faq_data:
    FAQ.objects.update_or_create(question_ar=q_ar, defaults=dict(
        question_ar=q_ar, question_en=q_en, answer_ar=a_ar, answer_en=a_en, order=order, is_published=True))

# ---- السياسات / الصفحات القانونية (بنية جاهزة، غير منشورة — بلا نص مخترع) ----
# ⚠️ ما منكتب نص قانوني هون. منجهّز الهيكل فقط. الأدمن يضيف النص المعتمد
#    بأقسام كل سياسة، وبعدها يفعّل is_published. لحد هيك: ما إلها رابط ولا صفحة.
from core.models import Policy, PolicySection  # noqa: E402

policies_scaffold = [
    ("privacy", "سياسة الخصوصية", "Privacy Policy", 1,
     ["مقدمة", "البيانات التي نجمعها", "كيف نستخدم بياناتك", "مشاركة البيانات", "حقوقك"]),
    ("terms", "الشروط والأحكام", "Terms & Conditions", 2,
     ["مقدمة", "الاشتراكات والتوصيل", "الدفع", "الإلغاء والاسترجاع", "حدود المسؤولية"]),
]
for slug, title_ar, title_en, order, section_headings in policies_scaffold:
    policy, _created = Policy.objects.update_or_create(
        slug=slug,
        defaults=dict(
            title_ar=title_ar, title_en=title_en, order=order,
            is_published=False,  # 🔴 لا تفعّلها إلا بعد إضافة النص القانوني المعتمد
            show_in_footer=True,
        ),
    )
    for i, heading in enumerate(section_headings):
        PolicySection.objects.get_or_create(
            policy=policy, order=i,
            defaults=dict(heading_ar=heading, body_ar=""),  # body فاضي = بانتظار النص المعتمد
        )

print("✅ تم تحميل بيانات Placeholder بنجاح.")
print("🔴 لا تنشر بدون تحديث رقم الواتساب والأسعار الحقيقية!")
print("📄 السياسات: أضف النص القانوني المعتمد من لوحة التحكم ثم فعّل «منشورة».")
