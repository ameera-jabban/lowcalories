from django.urls import path

from . import views

app_name = "corporate"

urlpatterns = [
    path("", views.corporate_page, name="corporate_page"),
]
