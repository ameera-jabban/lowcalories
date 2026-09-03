from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("subscriptions/", views.subscriptions_view, name="subscriptions"),
    path("progress/", views.progress_view, name="progress"),
    path("details/", views.personal_view, name="personal"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("freeze/", views.freeze_subscription, name="freeze"),
    path("resume/", views.resume_subscription, name="resume"),
    path("swap-meal-type/", views.swap_meal_type, name="swap_meal_type"),
    path("review/<str:access_code>/", views.leave_review, name="leave_review"),
]
