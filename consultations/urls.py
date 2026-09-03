from django.urls import path

from . import views

app_name = "consultations"

urlpatterns = [
    path("", views.consultations_list, name="list"),
]
