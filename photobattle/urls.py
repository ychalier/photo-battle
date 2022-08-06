from django.urls import path
from . import views

app_name = "photobattle"

urlpatterns = [
    path("", views.landing, name="landing"),
    path("battle/<code>/manage", views.manage_battle, name="manage_battle"),
    path("battle/<code>", views.view_battle, name="view_battle"),
    path("profile", views.view_profile, name="view_profile"),
    path("api", views.api, name="api"),
]