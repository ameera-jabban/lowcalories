from django.urls import path
from . import views

app_name = "plans"

urlpatterns = [
    path("", views.plans_list, name="plans_list"),
    path("build/", views.builder, name="builder"),
    path("validate-code/<str:code>/", views.validate_code, name="validate_code"),
]
