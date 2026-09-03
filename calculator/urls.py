from django.urls import path
from . import views

app_name = "calculator"

urlpatterns = [
    path("calorie-calculator/", views.calorie_calculator, name="calorie_calculator"),
    path("my-progress/", views.my_progress, name="my_progress"),
]
