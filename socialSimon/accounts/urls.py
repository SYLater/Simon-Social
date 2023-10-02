from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.login, name="login-page"),
    path("profile/", views.profile, name="profile"),
    path('display_image/', views.display_image, name='display_image')
    
]
