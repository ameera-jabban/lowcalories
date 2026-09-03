"""
تبسيط الاستشارات: إزالة نموذج الحجز القديم (أخصائي/موعد/حجز) بالكامل
وإضافة نموذج طلب استشارة بسيط. مشروع تطوير — ما في حجوزات إنتاج، الحذف آمن.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("consultations", "0002_nutritionist_name_localized"),
    ]

    operations = [
        migrations.AlterUniqueTogether(name="consultationslot", unique_together=set()),
        migrations.DeleteModel(name="ConsultationBooking"),
        migrations.DeleteModel(name="ConsultationSlot"),
        migrations.DeleteModel(name="Nutritionist"),
        migrations.CreateModel(
            name="ConsultationRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("full_name", models.CharField(max_length=120, verbose_name="الاسم الكامل")),
                ("phone", models.CharField(max_length=20, verbose_name="رقم الموبايل")),
                ("email", models.EmailField(blank=True, max_length=254, verbose_name="البريد الإلكتروني")),
                ("preferred_contact", models.CharField(
                    choices=[("whatsapp", "واتساب"), ("phone", "اتصال هاتفي"), ("email", "بريد إلكتروني")],
                    default="whatsapp", max_length=12, verbose_name="طريقة التواصل المفضّلة")),
                ("goal", models.CharField(max_length=200, verbose_name="الهدف / سبب الاستشارة")),
                ("notes", models.TextField(blank=True, verbose_name="ملاحظات إضافية")),
                ("language", models.CharField(blank=True, editable=False, max_length=5, verbose_name="اللغة")),
                ("source", models.CharField(
                    choices=[("consultations_page", "صفحة الاستشارات"), ("calculator_upsell", "بعد حاسبة السعرات"), ("other", "أخرى")],
                    default="consultations_page", editable=False, max_length=30, verbose_name="المصدر")),
                ("status", models.CharField(
                    choices=[("new", "جديد"), ("contacted", "تم التواصل"), ("scheduled", "تم تحديد موعد"), ("completed", "تمّت"), ("cancelled", "ملغى")],
                    default="new", max_length=12, verbose_name="الحالة")),
                ("admin_notes", models.TextField(blank=True, verbose_name="ملاحظات داخلية (للفريق فقط)")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الطلب")),
            ],
            options={
                "verbose_name": "طلب استشارة",
                "verbose_name_plural": "طلبات الاستشارات",
                "ordering": ["-created_at"],
            },
        ),
    ]
