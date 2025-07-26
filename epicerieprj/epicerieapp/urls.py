from django.urls import path
from django.contrib.auth import views as auth_views  # Import auth_views for logout
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("index/", views.index, name="index"),
    path(
        "applications/", views.applications_view, name="applications"
    ),  # Applications page URL
    path("about/", views.about, name="about"),
    path("clientdataentry/", views.clientdataentry, name="clientdataentry"),
    path("contact/", views.contact, name="contact"),
    path("vision/", views.vision, name="vision"),
    path("mission/", views.mission, name="mission"),
    path("apps/", views.apps, name="apps"),
    path("attendance/", views.attendance_view, name="attendance"),
    path("payroll/", views.payroll_view, name="payroll"),
    path("tasks/", views.tasks_management_view, name="tasks"),
    path("inventory/", views.inventory_view, name="inventory"),
    path("grocery/", views.online_grocery_view, name="grocery"),
    path("onlinetemp/", views.onlinetemp, name="onlinetemp"),
]
