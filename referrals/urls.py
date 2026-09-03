from django.urls import path

from . import views

app_name = "referrals"

urlpatterns = [
    path("referral/get-code/", views.get_code, name="get_code"),
    path("r/<str:code>/", views.claim, name="claim"),
]
