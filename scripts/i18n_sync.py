# -*- coding: utf-8 -*-
"""
مزامنة ترجمات الإنجليزية بدون GNU gettext.

الخلفية: هالبيئة ما فيها أدوات gettext (msgfmt/xgettext)، فأوامر Django
`makemessages` / `compilemessages` ما بتشتغل. هالسكربت بديل عملي:
    python scripts/i18n_sync.py
يدمج القاموس تحت (عربي → إنجليزي) في locale/en/LC_MESSAGES/django.po
ثم يجمّع django.mo عبر polib. idempotent — يملأ الفاضي فقط وما يلمس
الترجمات الموجودة.

لو عندك gettext مثبّت، تقدر تستخدم الطريقة القياسية بدله:
    python manage.py makemessages -l en && python manage.py compilemessages

عند إضافة سلاسل {% trans %} جديدة: أضف مدخلاتها لـ TRANSLATIONS تحت وشغّل السكربت.
"""
import os
import sys

import polib

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PO_PATH = os.path.join(_ROOT, "locale", "en", "LC_MESSAGES", "django.po")
MO_PATH = os.path.join(_ROOT, "locale", "en", "LC_MESSAGES", "django.mo")

# msgid عربي -> msgstr إنجليزي (سلاسل features specs 1)
TRANSLATIONS = {
    # ---- My Profile (customer hub) ----
    "حسابي": "My Account",
    "أهلاً بعودتك،": "Welcome back,",
    "تنقّل الحساب": "Account navigation",
    "نظرة عامة": "Overview",
    "الاشتراكات": "Subscriptions",
    "متابعة تقدّمي": "My Progress",
    "بياناتي": "Personal Details",
    "الإحالة والمكافآت": "Referral & Rewards",
    "تسجيل الخروج": "Log Out",
    "اشتراكات فعّالة": "Active subscriptions",
    "أيام متبقية": "Days remaining",
    "الخطة الحالية": "Current plan",
    "أقرب تاريخ انتهاء": "Next end date",
    "اشتراكاتك": "Your subscriptions",
    "إدارة الاشتراكات": "Manage subscriptions",
    "%(days)s يوم · %(meals)s وجبة/يوم": "%(days)s days · %(meals)s meals/day",
    "ينتهي": "Ends",
    "متبقّي %(n)s يوم": "%(n)s days remaining",
    "ما عندك اشتراك فعّال حالياً.": "No active subscriptions yet.",
    "اختر خطة تناسب هدفك ونكمّل معك من هناك.": "Choose a plan that fits your goals and we'll take it from there.",
    "ادعُ صديق — أول ما يشترك، الاثنين تاخدوا يوم مجاني.":
        "Invite a friend — when they subscribe, you both get a free day.",
    "بدأ": "Started",
    "%(done)s من %(total)s يوم": "%(done)s of %(total)s days",
    "%(n)s يوم متبقّي": "%(n)s days remaining",
    "إدارة الاشتراك": "Manage subscription",
    "بدك تغيّر شي باشتراكك؟ اختر إجراء وبنجهّزلك طلب واتساب لفريقنا.":
        "Need to change your subscription? Select an action and we'll prepare a WhatsApp request for our team.",
    "لتعديل بياناتك، راسل الفريق على واتساب ونحدّثها إلك.":
        "To update your details, message the team on WhatsApp and we'll change them for you.",
    "الاسم": "Name",
    "رقم الهاتف": "Phone number",
    "عضو منذ": "Member since",
    "من %(f)s إلى %(t)s": "From %(f)s to %(t)s",
    "كغ": "kg",
    "ما عندك سجل كافٍ للمقارنة بعد — احسب سعراتك مرة ثانية بعد كم أسبوع.":
        "Not enough history to compare yet — calculate your calories again in a few weeks.",
    "ما في سجل تقدّم بعد.": "No progress recorded yet.",
    "استخدم حاسبة السعرات واحفظ نتيجتك برقم هاتفك لتتابع رحلتك مع الوقت.":
        "Use the calorie calculator and save your result with your phone number to track your journey over time.",
    "احسب سعراتي": "Calculate my calories",

    # ---- accounts templates ----
    "اشتراكي": "My Subscription",
    "تسجيل خروج": "Log Out",
    "اشتراكك الحالي": "Your Current Subscription",
    "الحالة": "Status",
    "ينتهي بتاريخ": "Ends on",
    "إجراءات سريعة": "Quick Actions",
    "كل زر بيجهّزلك رسالة واتساب جاهزة — الفريق بيأكد الطلب معك.":
        "Each button prepares a ready WhatsApp message — the team confirms your request.",
    "تجميد الاشتراك": "Freeze Subscription",
    "استئناف الاشتراك": "Resume Subscription",
    "تغيير نوع الوجبات إلى": "Change meal type to",
    "اطلب التغيير": "Request Change",
    "ما عندك اشتراك مسجّل حالياً.": "You don't have an active subscription right now.",
    "شوف الخطط": "See Plans",
    "قيّم تجربتك": "Rate Your Experience",
    "وصلنا تقييمك ورح يظهر بالموقع بعد مراجعة سريعة من الفريق.":
        "We received your review — it will appear on the site after a quick check by the team.",
    "الصفحة الرئيسية": "Home",
    "أرسل التقييم": "Submit Review",
    "بوابة اشتراكي": "My Subscription Portal",  # لسا مستخدم برابط الفوتر
    "دخول": "Log In",
    # -- صفحة الدخول (إعادة تصميم: كرت مركزي مضغوط) --
    "إدارة اشتراكك": "Manage your subscription",
    "ادخل رقم هاتفك وكود الدخول لعرض وإدارة اشتراكك.":
        "Enter your phone number and access code to view and manage your subscription.",
    "تحتاج مساعدة؟": "Need help?",
    "ما عندك كود دخول؟": "Don't have an access code?",
    "تواصل مع فريقنا ومنبعتلك ياه.": "Contact our team and we'll send it to you.",
    "تواصل معنا على واتساب": "Contact us on WhatsApp",
    # ---- accounts blocktrans ----
    "أهلاً %(name)s 👋": "Hi %(name)s 👋",
    "متبقٍّ %(days)s يوم": "%(days)s days remaining",
    "مرحبا %(name)s، رأيك بيهمنا كتير.": "Hi %(name)s, your feedback means a lot to us.",
    # ---- accounts forms / views ----
    "رقم الهاتف": "Phone number",
    "كود الدخول": "Access code",
    "تقييمك": "Your rating",
    "رأيك بالتجربة": "Your experience",
    "رقم الهاتف أو كود الدخول غير صحيح.": "Phone number or access code is incorrect.",
    "ما في اشتراك فعّال يمكن تجميده.": "There is no active subscription to freeze.",
    "ما في اشتراك مجمّد يمكن استئنافه.": "There is no frozen subscription to resume.",
    "ما في اشتراك حالي لتغيير نوع وجباته.":
        "There is no current subscription to change the meal type for.",
    "مرحبا، أنا %(name)s. أرغب بتجميد اشتراكي (%(plan)s) اعتباراً من اليوم.":
        "Hello, I'm %(name)s. I'd like to freeze my subscription (%(plan)s) starting today.",
    "مرحبا، أنا %(name)s. أرغب باستئناف اشتراكي (%(plan)s). تاريخ الانتهاء الجديد بعد التمديد: %(end)s.":
        "Hello, I'm %(name)s. I'd like to resume my subscription (%(plan)s). "
        "New end date after the extension: %(end)s.",
    "مرحبا، أنا %(name)s. أرغب بتغيير نوع وجبات اشتراكي من %(old)s إلى %(new)s.":
        "Hello, I'm %(name)s. I'd like to change my subscription meal type from %(old)s to %(new)s.",
    # ---- corporate page (redesign) ----
    "خطط الشركات": "Corporate Plans",
    "وجبات صحية يومية لفريق شركتك، توصيل لموقع واحد وسعر واضح لكل موظف.":
        "Daily healthy meals for your company's team, delivered to one location with clear per-employee pricing.",
    "وجبات صحية يومية لفريق شركتك، توصيل لموقع واحد وسعر واضح لكل موظف. اطلب عرض سعر.":
        "Daily healthy meals for your team. Request a quote.",
    "وجبات صحية لفريقك،": "Healthy meals for your team,",
    "توصيل لمقر الشركة.": "delivered to the office.",
    "خطط وجبات مرنة للشركات — وجبات محسوبة السعرات، توصيل يومي، وسعر واضح لكل موظف.":
        "Flexible corporate meal plans — calorie-counted meals, daily delivery, and simple per-employee pricing.",
    "اطلب عرض سعر": "Request a Quote",
    "طلب عرض سعر": "Request a Quote",  # eyebrow قسم النموذج (اسم لا أمر)
    "مصمّمة للفرق": "Made for teams",
    "خطط وجبات بسيطة لشركات بأحجام مختلفة.": "Simple meal plans for companies of different sizes.",
    "منيو متنوّع": "Varied menu",
    "وجبات مختلفة محسوبة السعرات على مدار الأسبوع.": "Different calorie-counted meals throughout the week.",
    "توصيل لموقع واحد": "One delivery location",
    "توصيل كل الطلبات دفعة وحدة لمقر الشركة بالوقت المتفق عليه.":
        "Meals are delivered together to your office at the agreed time.",
    "سعر واضح لكل موظف": "Simple per-employee pricing",
    "تسعير واضح حسب حجم فريقك والخطة المختارة.": "Clear pricing based on your team size and selected plan.",
    "كيف تشتغل خطط الشركات": "How corporate plans work",
    "خبّرنا عن فريقك": "Tell us about your team",
    "ابعت بيانات شركتك وعدد الموظفين التقريبي.": "Submit your company details and approximate number of employees.",
    "نجهّز خطتك": "We prepare your plan",
    "فريقنا بيراجع متطلباتك ويجهّز العرض المناسب للشركات.":
        "Our team reviews your requirements and prepares the appropriate corporate offer.",
    "نتواصل معك": "We contact you",
    "فريقنا بيتواصل معك لتأكيد الخطة والسعر وتفاصيل التوصيل.":
        "Our team gets in touch to confirm the plan, pricing, and delivery details.",
    "خلّينا نبني الخطة المناسبة لفريقك.": "Let's build the right meal plan for your team.",
    "خبّرنا شوي عن شركتك وفريقنا بيتواصل معك بالخطة المناسبة.":
        "Tell us a little about your company and our team will contact you with the appropriate corporate plan.",
    "بدون التزام": "No commitment",
    "مفصّلة على حجم فريقك": "Tailored to your team size",
    "فريقنا بيتواصل معك مباشرة": "Our team will contact you directly",
    "استلمنا طلبك": "Request received",
    "شكراً — استلم فريقنا طلب وجبات شركتك وبيتواصل معك قريباً.":
        "Thanks — our team has received your corporate meal inquiry and will contact you shortly.",
    "تابع على واتساب": "Continue on WhatsApp",
    "اطلب استشارة": "Request a Consultation",
    "شارك بياناتك ونرجعلك قريباً.": "Share your details and we'll get back to you.",
    "أرسل طلب عرض السعر": "Request Corporate Quote",
    "ما في دفع بهالخطوة.": "No payment required at this step.",
    # ---- corporate forms ----
    "اسم الشركة": "Company name",
    "الشخص المسؤول": "Contact person",
    "رقم التواصل": "Contact phone",
    "عدد الموظفين التقريبي": "Approximate number of employees",
    "موقع التوصيل": "Delivery location",
    "ملاحظات (اختياري)": "Notes (optional)",

    # ==== الاستشارات (طلب بسيط — بدون أخصائي/مواعيد) ====
    "استشارة أخصائي تغذية": "Nutritionist Consultation",
    "اطلب استشارة تغذية وفريق Low Calories بيتواصل معك لترتيب الجلسة.":
        "Request a nutrition consultation and the Low Calories team will contact you to arrange it.",
    "اطلب استشارة وفريقنا بيتواصل معك لترتيب جلسة مع أخصائي تغذية — بتراجعوا فيها هدفك وسعراتك وبتطلع بخطة عملية مفصّلة عليك.":
        "Submit a request and our team will contact you to arrange a session with a nutritionist — "
        "you'll review your goal and calories together and leave with a practical, tailored plan.",
    "رسوم الجلسة %(price)s د.أ (يؤكّدها الفريق).": "Session fee %(price)s JOD (confirmed by the team).",
    "إرشاد تغذوي مخصّص لهدفك": "Personalized nutrition guidance",
    "دعم بخطة الوجبات وتوزيع الماكروز": "Meal-plan and macro-split support",
    "توصيات مبنية على وضعك وهدفك": "Goal-based recommendations",
    "اطلب استشارة": "Request a Consultation",
    "إرسال الطلب": "Submit Request",
    "ما في اختيار موعد — بعد ما تبعت الطلب، الفريق بيتواصل معك لترتيب الجلسة.":
        "No slot to pick — after you submit, the team contacts you to arrange the session.",
    "استلمنا طلب استشارتك": "Your consultation request has been received",
    "رح نتواصل معك قريباً لترتيب موعد الاستشارة.":
        "We'll contact you shortly to arrange your consultation.",
    "رقم الطلب: %(ref)s": "Request %(ref)s",
    "العودة للرئيسية": "Back to home",
    # -- إعادة تصميم الصفحة (عمودين: معلومات + كرت نموذج) --
    "استشارة تغذية": "Nutrition consultation",
    "إرشاد تغذوي مخصّص مبني على هدفك ونمط حياتك واحتياجك من السعرات. ابعت طلبك وفريقنا بيتواصل معك لترتيب الجلسة.":
        "Personalized nutrition guidance based on your goals, lifestyle, and calorie needs. "
        "Submit your request and our team will contact you to arrange your consultation.",
    "رسوم الاستشارة": "Consultation fee",
    "التفاصيل النهائية يؤكّدها فريقنا.": "Final details are confirmed by our team.",
    "ابعت طلبك": "Send your request",
    "نراجع تفاصيلك": "We review your details",
    "فريقنا بيتواصل معك": "Our team contacts you",
    "دخّل بياناتك وفريقنا بيتواصل معك.": "Leave your details and our team will get in touch.",
    "أرسل طلب الاستشارة": "Request Consultation",
    "ما في حجز أونلاين — فريقنا بيتواصل معك بعد مراجعة طلبك.":
        "No online booking required — our team will contact you after reviewing your request.",
    "استلمنا طلبك": "Request received",
    "شكراً — راح يراجع فريقنا تفاصيلك ويتواصل معك قريباً.":
        "Thank you. Our team will review your details and contact you shortly.",
    "خبّرنا باختصار عن هدفك — خسارة وزن، بناء عضل، تخطيط وجبات، إرشاد سعرات…":
        "Tell us briefly about your goal — weight loss, muscle gain, meal planning, calorie guidance, etc.",
    "بدك خطة مفصّلة عليك بالضبط؟ اطلب استشارة مع أخصائي تغذية.":
        "Want a plan tailored exactly to you? Request a consultation with a nutritionist.",
    # form fields + choices
    "الاسم الكامل": "Full Name",
    "رقم الموبايل": "Mobile Number",
    "البريد الإلكتروني": "Email",
    "طريقة التواصل المفضّلة": "Preferred Contact Method",
    "الهدف / سبب الاستشارة": "Goal / Reason for Consultation",
    "ملاحظات إضافية": "Additional Notes",
    "مثال: خسارة وزن، خطة وجبات، نصائح رياضية…": "e.g. weight loss, meal plan, training advice…",
    "واتساب": "WhatsApp",
    "اتصال هاتفي": "Phone Call",
    # status labels (customer-facing not really, but admin)
    "جديد": "New",
    "تم التواصل": "Contacted",
    "تم تحديد موعد": "Scheduled",
    "تمّت": "Completed",
    "ملغى": "Cancelled",

    # ==== Spec 3: referrals ====
    "ادعُ صاحبك واكسبوا يوم مجاني": "Invite a friend and both get a free day",
    "شارك رابطك الخاص — أول ما صاحبك يشترك لأول مرة، الاثنين تاخدوا يوم مجاني على اشتراككم.":
        "Share your personal link — as soon as your friend subscribes for the first time, "
        "you both get a free day on your subscription.",
    "كودك جاهز": "Your code is ready",
    "رابط المشاركة": "Share link",
    "شارك على واتساب": "Share on WhatsApp",
    "أنشئ كودي": "Create My Code",
    "اسمك": "Your name",
    "رقم هاتفك": "Your phone number",
    "دعوة صديق": "Friend Invite",
    "صديقك %(name)s دعاك!": "Your friend %(name)s invited you!",
    "اشترك لأول مرة عبر هالدعوة، والاثنين تاخدوا يوم مجاني على اشتراككم.":
        "Subscribe for the first time through this invite, and you both get a free day.",
    "أكمل عبر واتساب": "Continue on WhatsApp",
    "رح ننقلك لواتساب برسالة فيها كود الإحالة — الفريق بيأكد ويطبّق العرض.":
        "We'll take you to WhatsApp with the referral code — the team confirms and applies the offer.",
    "رابط غير صالح": "Invalid link",
    "هذا الرابط غير صالح": "This link is not valid",
    "كود الإحالة مش موجود أو انتهى. تواصل مع صاحبك ليبعتلك رابط جديد، أو اشترك مباشرة.":
        "The referral code doesn't exist or has expired. Ask your friend for a new link, "
        "or subscribe directly.",
    "بدعوتك تجرّب Low Calories Jordan! اشترك لأول مرة عبر رابطي وناخد الاثنين يوم مجاني:\n%(url)s":
        "I'm inviting you to try Low Calories Jordan! Subscribe for the first time through "
        "my link and we both get a free day:\n%(url)s",
    "مرحبا! صديقي %(referrer)s دعاني لـ Low Calories Jordan (كود الإحالة: %(code)s). بدي أشترك لأول مرة.":
        "Hi! My friend %(referrer)s invited me to Low Calories Jordan (referral code: "
        "%(code)s). I'd like to subscribe for the first time.",

    # ==== Spec 3: discount code (plans page) ====
    "عندك كود خصم؟": "Have a discount code?",
    "تطبيق": "Apply",
    "السعر المخفّض استرشادي — الفريق بيأكد الخصم النهائي على واتساب.":
        "The discounted price is for reference — the team confirms the final discount on WhatsApp.",
    "هذا الكود غير صالح أو منتهي.": "This code is not valid or has expired.",
    "تعذّر التحقق، حاول مجدداً.": "Couldn't verify — please try again.",

    # ==== Spec 3: progress tracking (calculator) ====
    "كود متابعة تقدّمك": "Your progress tracking code",
    "احفظه — بتحتاجه لتشوف تقدّمك لاحقاً من صفحة «متابعة تقدّمي».":
        "Save it — you'll need it to check your progress later from the “My Progress” page.",
    "متابعة تقدّمي": "My Progress",
    "ادخل رقم هاتفك وكود المتابعة لتشوف تاريخ حساباتك والمقارنة بينها.":
        "Enter your phone number and tracking code to see your calculation history and comparison.",
    "اعرض تقدّمي": "Show My Progress",
    "بيانات غير صحيحة.": "Invalid details.",
    "التاريخ": "Date",
    "الوزن (كغ)": "Weight (kg)",
    "السعرات": "Calories",
    "الهدف": "Goal",
    "ما عندك سجل كافٍ للمقارنة بعد — ارجع بعد كم أسبوع واحسب مرة ثانية.":
        "You don't have enough history to compare yet — come back in a few weeks and calculate again.",
    "من %(f)s إلى %(t)s: وزنك تغيّر من %(fw)s كغ إلى %(tw)s كغ.":
        "From %(f)s to %(t)s: your weight changed from %(fw)s kg to %(tw)s kg.",
    "رقم هاتفك (اختياري) — احفظ نتيجتك لتقارنها المرة الجاية":
        "Your phone number (optional) — save your result to compare it next time",
    "كود المتابعة": "Tracking code",

    # ==== Spec 4: premium UI ====
    "التنقل الرئيسي": "Main navigation",
    "افتح القائمة": "Open menu",
    "قائمة التنقل": "Navigation menu",
    "أغلق القائمة": "Close menu",
    "تواصل واتساب": "Contact on WhatsApp",
    "سياسة الخصوصية": "Privacy Policy",
    "ليش تختارنا؟": "Why choose us?",
    "بياناتك": "Your Info",
    "نشاطك وهدفك": "Your Activity & Goal",
    "اطبع النتيجة أو احفظها PDF": "Print the result or save as PDF",
    "آراء عملائنا": "What our customers say",
    "طبق وجبة صحية من Low Calories Jordan": "A healthy meal from Low Calories Jordan",

    # ==== Spec 5: Calo-inspired redesign ====
    "الأسئلة الشائعة": "FAQ",
    "أشهر خطة:": "Most popular plan:",
    "تحكّم كامل، ومرونة تامّة": "Total control. Full flexibility.",
    "كيف يعمل؟": "How it works",
    "ما لقيت جوابك؟ راسلنا على واتساب.": "Didn't find your answer? Message us on WhatsApp.",
    "لسا ما في أسئلة شائعة — راسلنا على واتساب لأي استفسار.":
        "No FAQs yet — message us on WhatsApp with any question.",
    "توزيع الماكروز": "Macro breakdown",
    "كل الأسئلة الشائعة": "All FAQs",
    "عمّان، الأردن": "Amman, Jordan",
    "الشروط والأحكام": "Terms & Conditions",

    # ==== Fix: navigation links for feature pages ====
    "حسابي": "My Account",
    "خدمات": "Services",
    "برنامج الإحالة": "Referral Program",
    "ادعُ صديق واكسبوا يوم مجاني": "Invite a friend and both get a free day",
    "شارك رابطك الخاص — أول ما صاحبك يشترك لأول مرة، الاثنين تاخدوا يوم مجاني.":
        "Share your personal link — as soon as your friend subscribes for the first time, you both get a free day.",
    "احصل على رابط الإحالة": "Get your referral link",

    # ==== صفحة الإحالة (get-code) — إعادة تصميم ====
    "ادعُ صديق": "Refer a friend",
    "ادعُ صديق.": "Invite a friend.",
    "الاثنين تاخدوا يوم مجاني.": "You both get a free day.",
    "شارك رابط الإحالة الخاص فيك — أول ما صاحبك يشترك، الاثنين تاخدوا يوم مجاني.":
        "Share your personal referral link — when your friend subscribes, you both get a free day.",
    "شارك رابط الإحالة الخاص فيك. أول ما صاحبك يشترك لأول مرة، الاثنين تاخدوا يوم مجاني على اشتراككم.":
        "Share your personal referral link. When your friend subscribes for the first time, you both receive a free day.",
    "شارك رابطك": "Share your link",
    "ابعت رابط الإحالة الخاص فيك لصاحبك.": "Send your personal referral link to a friend.",
    "صاحبك يشترك": "They subscribe",
    "صاحبك يكمّل أول اشتراك إله.": "Your friend completes their first subscription.",
    "الاثنين تستفيدوا": "You both benefit",
    "كل واحد فيكم بياخد يوم مجاني.": "You both receive a free day.",
    "جاهز للمشاركة": "Ready to share",
    "كود الإحالة الخاص فيك": "Your referral code",
    "نسخ الكود": "Copy code",
    "انسخ الكود": "Copy code",
    "تم النسخ": "Copied",
    "رابط الإحالة الخاص فيك": "Your referral link",
    "رابط الإحالة": "Referral link",
    "انسخ الرابط": "Copy link",
    "نسخ": "Copy",
    "احصل على كود الإحالة الخاص فيك": "Get your referral code",
    # -- صفحة قبول الدعوة (/r/<code>/) --
    "%(name)s دعاك إلى Low Calories": "%(name)s invited you to Low Calories",
    "اشترك لأول مرة عبر هالدعوة والاثنين تاخدوا يوم مجاني.":
        "Subscribe for the first time through this invite and you both get a free day.",
    "%(name)s دعاك إلى": "%(name)s invited you to",
    "انضم عبر دعوة %(name)s، وأول ما تبدأ أول اشتراك إلك، الاثنين تاخدوا يوم مجاني.":
        "Join through %(name)s's invitation and when you start your first subscription, you both get a free day.",
    "يوم مجاني": "free day",
    "إلك": "For you",
    "لصاحبك": "For your friend",
    "دخّل بياناتك": "Enter your details",
    "أكمل عبر واتساب": "Continue on WhatsApp",
    "اشترك واستلم يومك المجاني": "Subscribe and receive your free day",
    "احصل على يومك المجاني": "Claim your free day",
    "دخّل بياناتك ومنجهّزلك طلب الإحالة.": "Enter your details and we'll prepare your referral request.",
    "منجهّزلك طلب الإحالة ونفتح واتساب — الفريق بيأكد العرض معك. ما في دفع بهالخطوة.":
        "We'll prepare your referral request and open WhatsApp. Our team will confirm the offer with you. No payment at this step.",

    # ==== حاسبة السعرات — تسميات وخيارات الفورم (كانت hardcoded عربي) ====
    "الجنس": "Gender",
    "العمر": "Age",
    "الطول (سم)": "Height (cm)",
    "الوزن (كغ)": "Weight (kg)",
    "مستوى النشاط": "Activity level",
    "هدفك": "Your goal",
    "ذكر": "Male",
    "أنثى": "Female",
    "خسارة وزن": "Lose weight",
    "تثبيت الوزن": "Maintain weight",
    "بناء عضل": "Build muscle",
    "قليل الحركة (مكتب، بدون رياضة)": "Sedentary (desk job, no exercise)",
    "نشاط خفيف (رياضة 1-3 أيام بالأسبوع)": "Lightly active (exercise 1–3 days/week)",
    "نشاط متوسط (رياضة 4-5 أيام بالأسبوع)": "Moderately active (exercise 4–5 days/week)",
    "نشيط (رياضة يومية أو مكثفة 3-4 أيام)": "Active (daily exercise, or intense 3–4 days)",
    "نشيط جداً (رياضة مكثفة 6-7 أيام)": "Very active (intense exercise 6–7 days)",
    "رياضي محترف أو عمل بدني شاق يومياً": "Athlete, or heavy physical work daily",

    # ==== رسائل واتساب الجاهزة (تُترجم حسب لغة الزائر) ====
    "مرحبا، بدي أسأل عن Low Calories Jordan": "Hi, I'd like to ask about Low Calories Jordan",
    "مرحبا، أريد الاشتراك في خطة %(days)s يوم - %(type)s %(meals)s وجبة (%(price)s د)":
        "Hi, I'd like to subscribe to the %(days)s-day plan - %(type)s, %(meals)s meals (%(price)s JOD)",
    "كود خصم: %(code)s (-%(pct)s%%) — السعر بعد الخصم تقريباً %(new)s د بدل %(old)s د":
        "Discount code: %(code)s (-%(pct)s%%) — price after discount approx. %(new)s JOD instead of %(old)s JOD",

    # ==== نظام السياسات / الصفحات القانونية ====
    "آخر تحديث: %(d)s": "Last updated: %(d)s",
    "النسخة %(v)s": "Version %(v)s",
    "للتواصل معنا": "Contact Us",
    "لأي استفسار بخصوص هذه الصفحة، تواصل مع %(name)s:":
        "For any questions about this page, contact %(name)s:",
    "واتساب": "WhatsApp",
    "البريد الإلكتروني": "Email",
    "الموقع": "Location",
    "ساعات العمل": "Working Hours",

    # ==== قسم الأسئلة الشائعة (الصفحة الرئيسية + /faq) ====
    "عندك أسئلة؟": "Still have questions?",
    "شوف الأسئلة الشائعة": "Check out our FAQ",
    "عندك سؤال ثاني؟": "Got more questions?",
    "فريقنا جاهز يساعدك — راسلنا على واتساب وبنرد عليك بأسرع وقت.":
        "Our team is here to help — message us on WhatsApp and we'll get back to you shortly.",
    "تواصل على واتساب": "Chat on WhatsApp",
    "عرض كل الأسئلة الشائعة": "View all FAQs",
    "مرحبا، عندي سؤال عن Low Calories Jordan": "Hi, I have a question about Low Calories Jordan",
    "أجوبة على أكثر الأسئلة تكراراً عن خطط Low Calories Jordan، الاشتراك، التوصيل، والدفع.":
        "Answers to the most common questions about Low Calories Jordan plans, subscriptions, delivery, and payment.",

    # ==== قسم "تحكّم كامل، مرونة تامّة" (سبليت) ====
    "تحكّم كامل.": "Total control.",
    "مرونة تامّة.": "Full flexibility.",
    "سعرات وماكروز تناسب هدفك بالضبط.": "Calories and macros that match your goals.",
    "اختر يلي بتحبه، وبدّل يلي ما بتحبه.": "Choose what you like. Swap what you don't.",
    "جمّد. تخطَّ. غيّر. وقت ما بدك.": "Pause. Skip. Change. Anytime.",
    "حياتك بتتغيّر وخطتك بتتغيّر معك — عدّل لحد ٢٤ ساعة قبل التوصيل بدون أي تعقيد.":
        "Life changes and your plan can too. Adjust up to 24 hours before delivery, no hassle.",
    "أي أيام بتحب توصلك وجبات Low Calories؟": "Which days do you want Low Calories meals?",
    "أحد": "Sun", "إثنين": "Mon", "ثلاثاء": "Tue", "أربعاء": "Wed", "خميس": "Thu", "جمعة": "Fri", "سبت": "Sat",
    "العنوان": "Address",
    "البيت": "Home",
    "الوقت": "Time",
    "٧ ص – ١١ ص": "7 AM – 11 AM",
    "التوصيل متخطّى ليوم الأربعاء": "Delivery skipped for Wednesday",
    "مثال توضيحي لإدارة أيام التوصيل": "Illustration of delivery-day management",

    # ==== كيف يعمل ====
    "توصل لهدفك بثلاث خطوات بسيطة.": "Reach your goal in three simple steps.",
    "الخطوة %(n)s:": "Step %(n)s:",

    # ==== كاروسيل الخطط (الصفحة الرئيسية) ====
    "لاقِ خطتك المثالية": "Find your perfect meal plan",
    "شوف كل الخطط": "See all plans",
    "تبدأ من %(price)s د.أ": "Starting from %(price)s JOD",
    "الأكثر طلباً": "Most Popular",
    "بروتين": "Protein",
    "كارب": "Carbs",
    "دهون": "Fat",
    "تبدأ من": "Starting from",
    "%(g)sغ": "%(g)sg",
    "الخطط السابقة": "Previous plans",
    "الخطط التالية": "Next plans",
    "وجبات سابقة": "Previous meals",
    "وجبات تالية": "Next meals",

    # ==== مقتطف المنيو الأسبوعي (الصفحة الرئيسية) ====
    "منيو يتجدّد كل أسبوع": "A menu that changes every week",
    "وجبات طازة محسوبة السعرات، جاهزة لأسبوعك.": "Fresh, calorie-counted meals ready for your week.",
    "سعرات محسوبة": "Calorie counted",
    "مكوّنات طازة": "Fresh ingredients",
    "خيارات بروتين متعددة": "Multiple protein options",
    "يتجدّد كل أسبوع": "Updated weekly",
    "شوف المنيو الكامل": "See full menu",
    "%(c)s سعرة": "%(c)s kcal",
    "%(g)sغ بروتين": "%(g)sg protein",
    "%(g)sغ كارب": "%(g)sg carbs",
    "%(g)sغ دهون": "%(g)sg fat",

    # ==== قصص العملاء ====
    "نتائج حقيقية، قصص حقيقية": "Real results, real stories",
    "موثوقون من مجتمع Low Calories": "Trusted by our Low Calories community",
    "★ %(rating)s — %(count)s تقييم": "★ %(rating)s — %(count)s reviews",
    "%(r)s من 5": "%(r)s out of 5",
    "نوصّل لـ %(count)s منطقة داخل عمّان": "Delivering to %(count)s areas across Amman",

    # ==== هيرو الصفحة الرئيسية ====
    "شوف المنيو": "View Menu",
    "انتقل للقسم التالي": "Scroll to next section",
    "انتقل إلى خطط الوجبات": "Scroll to meal plans",
    "تغيير اللغة": "Change language",
    "اللغة": "Language",
    "ابدأ رحلتك الصحية اليوم": "Start your healthy journey today",
    "الأحد": "Sunday", "الاثنين": "Monday", "الثلاثاء": "Tuesday", "الأربعاء": "Wednesday",
    "الخميس": "Thursday", "الجمعة": "Friday", "السبت": "Saturday",
    "مقدمة": "Introduction",

    # ==== مُكوّن خطة الاشتراك (/plans/build) ====
    "اصنع خطتك المثالية": "Build your perfect plan",
    "اختر تفضيلاتك خطوة بخطوة وشوف السعر مباشرة.":
        "Choose your preferences step by step and see the price instantly.",
    "اختر نوع الخطة": "Choose your plan",
    "كم وجبة باليوم؟": "How many meals per day?",
    "اختر مدة الاشتراك": "Choose your subscription duration",
    "وجبة": "meal",
    "وجبات": "meals",
    "وجبة / اليوم": "meal / day",
    "وجبات / اليوم": "meals / day",
    "خطتك": "Your plan",
    "اختر تفضيلاتك ويظهر ملخّص خطتك هنا.": "Choose your preferences and your plan summary appears here.",
    "النوع": "Type",
    "الوجبات": "Meals",
    "المدة": "Duration",
    "المجموع": "Total",
    "متابعة عبر واتساب": "Continue on WhatsApp",
    "هذه التركيبة غير متاحة حالياً — جرّب خياراً آخر.":
        "This combination is currently unavailable — try another option.",
    "تبدأ من": "Starting from",

    # ==== التنقّل المركزي (core/navigation.py) ====
    "الرئيسية": "Home",
    "الخطط": "Plans",
    "المنيو الأسبوعي": "Weekly Menu",
    "حاسبة السعرات": "Calorie Calculator",
    "تواصل معنا": "Contact Us",
    "روابط سريعة": "Quick Links",

    # ==== مراجعة الترجمة الشاملة — سلاسل كانت تظهر عربي على /en/ ====
    # -- هيرو الصفحة الرئيسية --
    "اشتراك وجبات صحية — عمّان، الأردن": "Healthy meal subscription — Amman, Jordan",
    "سعرات محسوبة، ماكروز مضبوطة، وتوصيل يومي داخل عمّان.":
        "Calorie-counted meals, precise macros, and daily delivery across Amman.",
    "اطلب الآن": "Order Now",
    # -- حاسبة السعرات (إعادة تصميم) --
    "احسب سعراتك اليومية وماكروزك، ولاقِ الخطة اللي تناسب هدفك.":
        "Calculate your daily calories and macros, and find the plan that fits your goal.",
    "احسب سعراتي": "Calculate My Calories",
    "اعرف شو جسمك بيحتاج": "Know what your body needs",
    "بنحسبلك هدف يومي مبني على:": "We calculate a daily target based on:",
    "عمرك وقياسات جسمك": "Your age and body measurements",
    "مستوى نشاطك": "Your activity level",
    "هدفك الحالي": "Your current goal",
    "وبعد الحساب بنعرضلك:": "After calculating, we'll show you:",
    "السعرات اليومية": "Daily calories",
    "البروتين والكارب والدهون": "Protein, carbs and fat",
    "الخطة اللي تناسب هدفك": "The plan that fits your goal",
    "هدفك اليومي": "Your daily target",
    "%(d)s يوم": "%(d)s days",
    "%(m)s وجبة/يوم": "%(m)s meals/day",
    # -- حاسبة السعرات --
    "حاسبة السعرات الحرارية": "Calorie Calculator",
    "احسب سعراتك وماكروزك بدقة، واحصل فوراً على خطة اشتراك مناسبة.":
        "Calculate your calories and macros precisely, and get a matching subscription plan instantly.",
    "احسب سعراتي 🔥": "Calculate My Calories",
    "نتيجتك": "Your Result",
    "سعرة/يوم": "kcal/day",
    "كربوهيدرات": "Carbs",
    "الخطة المقترحة إلك": "Your Suggested Plan",
    "يوم": "days",
    "وجبة": "meals",
    "د.أ": "JOD",
    "ابعتلي هالخطة على واتساب": "Send me this plan on WhatsApp",
    "شوف وجبات هذا الأسبوع": "See this week's meals",
    # -- صفحة الخطط (إعادة تصميم) --
    "خطط وأسعار": "Plans & Pricing",
    "اختار الخطة اللي تناسب روتينك.": "Choose the plan that fits your routine.",
    "حدّد عدد الأيام، نوع الوجبات، وعدد الوجبات باليوم.":
        "Select your number of days, meal type, and meals per day.",
    "اختار الخطة اللي تناسب روتينك — حدّد عدد الأيام، نوع الوجبات، وعدد الوجبات باليوم.":
        "Choose the plan that fits your routine — select your number of days, meal type, and meals per day.",
    "أدخل الكود": "Enter code",
    "وجبة واحدة / اليوم": "1 meal / day",
    "%(n)s وجبات / اليوم": "%(n)s meals / day",
    "اشترك الآن": "Subscribe Now",
    "الخطط غير متوفرة حالياً — تواصل معنا على واتساب.":
        "Plans aren't available right now — contact us on WhatsApp.",
    # -- المنيو الأسبوعي (إعادة تصميم الصفحة) --
    "وجبات طازة محسوبة السعرات، تتجدد كل أسبوع.": "Fresh, calorie-counted meals, updated every week.",
    "وجبات طازة محسوبة السعرات، جاهزة لأسبوعك.": "Fresh, calorie-counted meals ready for your week.",
    "هذا الأسبوع": "This week",
    "أسبوع %(d)s": "Week of %(d)s",
    "أيام الأسبوع": "Days of the week",
    # -- المنيو الأسبوعي --
    "منيو أسبوع": "Menu for week of",
    "يتجدد كل أحد": "Updated every Sunday",
    "سعرة": "kcal",
    "المنيو غير متوفر حالياً — تواصل معنا على واتساب لمعرفة وجبات هذا الأسبوع.":
        "The menu isn't available right now — contact us on WhatsApp for this week's meals.",
    "خليه يوصلك كل يوم": "Get it delivered every day",
    "شوف خطط الاشتراك": "See subscription plans",
    "شوف الخطط الأسبوعية": "See weekly plans",
    # -- عام / مشترك --
    "التنقل": "Navigation",
    "السابق": "Previous",
    "التالي": "Next",
    "شكراً إلك! 🙏": "Thank you!",
    # -- حالة الاشتراك (Subscription.Status) --
    "فعّال": "Active",
    "مجمّد": "Paused",
    "منتهي": "Expired",
    # -- لوحة التحكم / إدارة الاستشارات (تظهر للأدمن فقط، لكن نترجمها للاتساق) --
    "لوحة القيادة": "Dashboard",
    "أخرى": "Other",
    "صفحة الاستشارات": "Consultations page",
    "بعد حاسبة السعرات": "After calorie calculator",
    "طلب استشارة": "Consultation request",
    "طلبات الاستشارات": "Consultation requests",
    "تاريخ الطلب": "Request date",
    "المصدر": "Source",
    "ملاحظات داخلية (للفريق فقط)": "Internal notes (team only)",
    "المرجع": "Reference",
    "الطلب": "Request",
    "بيانات العميل": "Customer info",
    "متابعة الفريق": "Team follow-up",
    "تواصل مع العميل": "Contact customer",
    "تواصل عبر واتساب": "Contact on WhatsApp",
    "بريد إلكتروني": "Email",
    # ملاحظة: "الاسم الكامل" / "رقم الموبايل" / "الهدف..." / "طريقة التواصل المفضّلة" / "اتصال هاتفي"
    # معرّفة مرّة واحدة بقسم حقول النماذج فوق (Title Case) — لا نكرّرها هون بحالة أحرف مختلفة.

    # ==== لوحة التحكم (Unfold): مجموعات الشريط الجانبي + لوحة القيادة ====
    "لوحة عمليات Low Calories": "Low Calories operations panel",
    "نظرة عامة": "Overview",
    "آخر التعديلات": "Recent changes",
    "العملاء والطلبات": "Customers & requests",
    "العملاء": "Customers",
    "طلبات الاستشارات": "Consultation requests",
    "طلبات عروض الشركات": "Corporate quote requests",
    "الإحالات": "Referrals",
    "أكواد الإحالة": "Referral codes",
    "الاشتراكات والتسعير": "Subscriptions & pricing",
    "خطط الاشتراك": "Subscription plans",
    "اشتراكات العملاء": "Customer subscriptions",
    "نوايا الشراء (Leads)": "Purchase intents (Leads)",
    "أكواد الخصم": "Discount codes",
    "خطط الشركات": "Corporate plans",
    "المنيو والتغذية": "Menu & nutrition",
    "أنواع الوجبات": "Meal types",
    "نتائج حاسبة السعرات": "Calorie calculator results",
    "التوصيل": "Delivery",
    "مناطق التوصيل": "Delivery areas",
    "المحتوى والإعدادات": "Content & settings",
    "إعدادات الموقع": "Site settings",
    "محتوى الـ Hero": "Hero content",
    "كيف يعمل": "How it works",
    "تقييمات العملاء": "Customer testimonials",
    "مزايا الموقع": "Site features",
    "السياسات القانونية": "Legal policies",
    "المستخدمون والصلاحيات": "Users & permissions",
    "المستخدمون": "Users",
    "الأدوار": "Roles",
    # لوحة القيادة
    "شو يحتاج انتباه اليوم؟": "What needs attention today?",
    "كل التعديلات": "All changes",
    "لا توجد بيانات لعرضها بصلاحياتك الحالية.": "No data to show with your current permissions.",
    "نوايا الشراء — آخر 7 أيام": "Purchase intents — last 7 days",
    "آخر نشاط الفريق": "Recent team activity",
    "عرض الكل": "View all",
    "بواسطة %(u)s": "by %(u)s",
    "لا يوجد نشاط مُسجّل بعد.": "No activity recorded yet.",
    "طلبات استشارة جديدة": "New consultation requests",
    "بانتظار تواصل الفريق": "Awaiting team contact",
    "طلبات عروض شركات جديدة": "New corporate quote requests",
    "آخر 7 أيام": "Last 7 days",
    "اشتراكات فعّالة": "Active subscriptions",
    "إحالات بانتظار التأكيد": "Referrals awaiting confirmation",
    "نوايا شراء اليوم": "Purchase intents today",
    "إجمالي %(n)s": "%(n)s total",
    "استخدامات حاسبة السعرات": "Calorie calculator uses",
    # صفحة "آخر 20 تعديل"
    "آخر 20 تعديل عبر الموقع": "Last 20 changes across the site",
    "الإجراء": "Action",
    "العنصر": "Item",
    "الحقول المعدّلة": "Changed fields",
    "المستخدم": "User",
    "التاريخ": "Date",
    "(بدون مستخدم)": "(no user)",
    "لا يوجد أي تعديل مُسجّل بعد على الموديلات المتتبَّعة.":
        "No changes recorded yet on the tracked models.",

    # ==== أسماء الموديلات (verbose_name) — تظهر بالشريط الجانبي/breadcrumbs/عناوين ====
    "عميل": "Customer",
    "اشتراك": "Subscription",
    "خطة اشتراك": "Subscription plan",
    "منطقة توصيل": "Delivery area",
    "كود خصم": "Discount code",
    "نوع وجبة": "Meal type",
    "منيو أسبوعي": "Weekly menu",
    "خطة شركات": "Corporate plan",
    "طلب عرض سعر شركة": "Corporate quote request",
    "طلبات عروض أسعار الشركات": "Corporate quote requests",
    "كود إحالة": "Referral code",
    "إحالة": "Referral",
    "نية شراء (Lead)": "Purchase intent (Lead)",
    "نتيجة حاسبة سعرات": "Calorie calculation",
    "تقييم عميل": "Customer testimonial",
    "هدف (Hero)": "Hero goal",
    "أهداف الـ Hero المتغيّرة": "Rotating hero goals",
    "خطوة (كيف يعمل)": "How-it-works step",
    "خطوات «كيف يعمل»": "How-it-works steps",
    "سؤال شائع": "FAQ",
    "الأسئلة الشائعة (FAQ)": "FAQs",
    "ميزة (ليش تختارنا)": "Site feature",
    "مزايا (ليش تختارنا)": "Site features",
    "سياسة / صفحة قانونية": "Legal policy / page",
    "السياسات والصفحات القانونية": "Legal policies & pages",
    "قسم سياسة": "Policy section",
    "أقسام السياسة": "Policy sections",
    "إعدادات الموقع": "Site settings",
    # ==== تسميات الحقول (verbose_name) — رؤوس الجداول + نماذج التعديل ====
    "الاسم (عربي)": "Name (Arabic)",
    "الاسم (إنجليزي)": "Name (English)",
    "العنوان (عربي)": "Title (Arabic)",
    "العنوان (إنجليزي)": "Title (English)",
    "الوصف (عربي)": "Description (Arabic)",
    "الوصف (إنجليزي)": "Description (English)",
    "النص (عربي)": "Text (Arabic)",
    "النص (إنجليزي)": "Text (English)",
    "السؤال (عربي)": "Question (Arabic)",
    "السؤال (إنجليزي)": "Question (English)",
    "الجواب (عربي)": "Answer (Arabic)",
    "الجواب (إنجليزي)": "Answer (English)",
    "التصنيف (إنجليزي)": "Category (English)",
    "الموقع (اختياري)": "Location (optional)",
    "الموقع (إنجليزي)": "Location (English)",
    "الخطة (اختياري)": "Plan (optional)",
    "الخطة (إنجليزي)": "Plan (English)",
    "وصف SEO (عربي)": "SEO description (Arabic)",
    "وصف SEO (إنجليزي)": "SEO description (English)",
    "عنوان القسم (عربي)": "Section heading (Arabic)",
    "عنوان القسم (إنجليزي)": "Section heading (English)",
    "الفقرات (عربي)": "Body (Arabic)",
    "الفقرات (إنجليزي)": "Body (English)",
    "عناصر القائمة (عربي)": "List items (Arabic)",
    "عناصر القائمة (إنجليزي)": "List items (English)",
    "نوع القائمة": "List type",
    "الترتيب": "Order",
    "مفعّل": "Active",
    "مفعّلة": "Active",
    "منشور": "Published",
    "منشورة": "Published",
    "الأيقونة": "Icon",
    "المُعرّف": "Slug",
    "المعرّف بالرابط": "URL slug",
    "رمز تعبيري": "Emoji",
    "الصورة": "Image",
    "صورة الخطة": "Step image",
    "صورة العميل (اختياري)": "Customer photo (optional)",
    "تظهر بروابط الفوتر": "Show in footer links",
    "يظهر بمقتطف الصفحة الرئيسية": "Show in homepage preview",
    "مميّز (يظهر بالصفحة الرئيسية)": "Featured (shown on homepage)",
    "رقم النسخة (اختياري)": "Version number (optional)",
    "آخر تحديث": "Last updated",
    # أسماء العملاء/الاشتراكات/التواصل
    "الاسم": "Name",
    "رقم الهاتف": "Phone number",
    "كود الدخول": "Access code",
    "تاريخ الإنشاء": "Created at",
    "الحالة": "Status",
    "الخطة": "Plan",
    "العميل": "Customer",
    "تاريخ البداية": "Start date",
    "تاريخ الانتهاء": "End date",
    "تاريخ التجميد": "Freeze date",
    "تاريخ إرسال طلب التقييم": "Review request sent at",
    "اسم صاحب الكود": "Referrer name",
    "رقم هاتفه": "Referrer phone",
    "الكود": "Code",
    "اسم الصديق": "Friend's name",
    "رقم هاتف الصديق": "Friend's phone",
    "كود الإحالة": "Referral code",
    "تاريخ الاستبدال": "Redeemed at",
    "بانتظار": "Pending",
    "تم الاستبدال": "Redeemed",
    # شركات
    "اسم الشركة": "Company name",
    "الشخص المسؤول": "Contact person",
    "رقم التواصل": "Contact phone",
    "عدد الموظفين التقريبي": "Approx. employee count",
    "موقع التوصيل": "Delivery location",
    "ملاحظات": "Notes",
    "أقل عدد موظفين": "Min employees",
    "أكثر عدد موظفين": "Max employees",
    "سعر الموظف (د.أ)": "Price per employee (JOD)",
    "نوع الوجبة": "Meal type",
    "الوصف": "Description",
    # خطط/خصومات/توصيل
    "عدد الأيام": "Days",
    "وجبات باليوم": "Meals per day",
    "السعر (د.أ)": "Price (JOD)",
    "الأكثر طلباً": "Most popular",
    "نسبة الخصم %": "Discount %",
    "صالح حتى": "Valid until",
    "أقصى عدد استخدامات": "Max uses",
    "عدد الاستخدامات": "Uses count",
    # منيو
    "تاريخ بداية الأسبوع": "Week start date",
    "المنيو الأسبوعي": "Weekly menu",
    "يوم الأسبوع": "Day of week",
    "السعرات": "Calories",
    "بروتين (غ)": "Protein (g)",
    "كربوهيدرات (غ)": "Carbs (g)",
    "دهون (غ)": "Fat (g)",
    "بروتين %": "Protein %",
    "كربوهيدرات %": "Carbs %",
    "دهون %": "Fat %",
    # حاسبة السعرات
    "الجنس": "Gender",
    "العمر": "Age",
    "الطول (سم)": "Height (cm)",
    "الوزن (كغ)": "Weight (kg)",
    "مستوى النشاط": "Activity level",
    "الهدف": "Goal",
    "السعرات الناتجة": "Result calories",
    "الخطة المقترحة": "Suggested plan",
    "كود المتابعة": "Progress code",
    # leads
    "صفحة المصدر": "Source page",
    "كود الخصم المستخدم": "Discount code used",
}


def main():
    po = polib.pofile(PO_PATH)
    existing = {e.msgid: e for e in po}
    added, updated, skipped = 0, 0, 0

    for msgid, msgstr in TRANSLATIONS.items():
        if msgid in existing:
            entry = existing[msgid]
            if entry.msgstr != msgstr:
                entry.msgstr = msgstr  # القاموس هو مصدر الحقيقة — أي اختلاف يُحدَّث
                updated += 1
            else:
                skipped += 1
        else:
            po.append(polib.POEntry(msgid=msgid, msgstr=msgstr))
            added += 1

    # تنظيف: احذف أي مدخل مش موجود بالقاموس (مفاتيح ميزات محذوفة — بلوك، حجز مواعيد...).
    # الـ .po هون مبني بالكامل من TRANSLATIONS (ما في gettext)، فأي orphan = مفتاح ميت.
    stale = [e for e in po if e.msgid and e.msgid not in TRANSLATIONS]
    for e in stale:
        po.remove(e)
    removed = len(stale)

    # تأكد ما ضل ولا msgstr فاضي
    empty = [e.msgid for e in po if not e.msgstr and e.msgid]
    po.save(PO_PATH)
    po.save_as_mofile(MO_PATH)

    print(f"added={added} filled={updated} kept={skipped} pruned={removed} total={len(po)}")
    if empty:
        print("STILL EMPTY:", empty)
        sys.exit(1)
    print("OK — django.po + django.mo written")


if __name__ == "__main__":
    main()
