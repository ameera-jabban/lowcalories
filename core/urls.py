from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("faq/", views.faq, name="faq"),
    path("policies/<slug:slug>/", views.policy_detail, name="policy"),
]
