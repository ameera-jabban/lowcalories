from django.urls import path
from . import views

app_name = "leads"

urlpatterns = [
    path("go/<int:plan_id>/", views.go_to_whatsapp, name="go_to_whatsapp"),
    path("go/", views.go_to_whatsapp_general, name="go_to_whatsapp_general"),
]
