from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="student-dashboard"),
    path("social/", views.social, name="social-board"),
]