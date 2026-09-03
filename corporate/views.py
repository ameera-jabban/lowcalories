"""
صفحة الشركات (B2B). نفس نمط leads/views.py حرفياً:
1) الفورم ينشئ CorporateInquiry بقاعدة البيانات
2) يحوّل المستخدم لواتساب برسالة جاهزة فيها كل التفاصيل
"""
from django.shortcuts import render

from core.models import SiteSettings
from .forms import CorporateInquiryForm


def corporate_page(request):
    """
    طلب عرض سعر للشركات — الفورم يخزّن CorporateInquiry ثم يعرض حالة نجاح
    مع زر واتساب برسالة جاهزة (نفس نمط طلب الاستشارة). الفريق يتواصل يدوياً.
    """
    submitted = None
    wa_url = ""

    if request.method == "POST":
        form = CorporateInquiryForm(request.POST)
        if form.is_valid():
            submitted = form.save()
            wa_url = SiteSettings.get_solo().whatsapp_link(submitted.whatsapp_message())
            form = CorporateInquiryForm()
    else:
        form = CorporateInquiryForm()

    return render(request, "corporate/corporate.html", {
        "form": form,
        "submitted": submitted,
        "wa_url": wa_url,
    })
