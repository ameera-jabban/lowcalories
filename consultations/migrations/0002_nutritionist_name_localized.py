from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("consultations", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="nutritionist",
            old_name="name",
            new_name="name_ar",
        ),
        migrations.AlterField(
            model_name="nutritionist",
            name="name_ar",
            field=models.CharField(max_length=120, verbose_name="الاسم (عربي)"),
        ),
        migrations.AddField(
            model_name="nutritionist",
            name="name_en",
            field=models.CharField(
                blank=True, max_length=120, verbose_name="الاسم (إنجليزي)",
                help_text="اسم الأخصائي بالحروف اللاتينية — يظهر للزوار على /en/. لو فاضي يظهر الاسم العربي.",
            ),
        ),
    ]
