"""
استشارة تغذية — صفحة تعريفية + فورم طلب. لا اختيار أخصائي/موعد.
العميل يرسل طلب → يُحفظ ويظهر للأدمن → الفريق يتواصل معه يدوياً.
"""
from django.shortcuts import render
from django.utils.translation import get_language

from core.models import SiteSettings
from .forms import ConsultationRequestForm
from .models import SOURCE_CHOICES

_VALID_SOURCES = {value for value, _label in SOURCE_CHOICES}


def _clean_source(raw: str) -> str:
    return raw if raw in _VALID_SOURCES else "consultations_page"


def consultations_list(request):
    """صفحة الاستشارة + فورم الطلب. بعد الإرسال بنجاح: حالة تأكيد بدل الفورم."""
    source = _clean_source(request.GET.get("source", request.POST.get("source", "")))
    submitted = None

    if request.method == "POST":
        form = ConsultationRequestForm(request.POST)
        if form.is_valid():
            submitted = form.save(commit=False)
            submitted.source = source
            submitted.language = (get_language() or "")[:5]
            submitted.save()
            form = ConsultationRequestForm()  # فورم نظيف (ما بينعرض بحالة النجاح)
    else:
        form = ConsultationRequestForm()

    return render(request, "consultations/list.html", {
        "form": form,
        "source": source,
        "submitted": submitted,
        "site_settings": SiteSettings.get_solo(),
    })
