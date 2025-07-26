from django.urls import path
from django.contrib.auth import views as auth_views  # Import auth_views for logout
from . import views

urlpatterns = [
     path('', views.home, name='home'),
     path('applications/', views.applications_view, name='applications'),  # Applications page URL
]