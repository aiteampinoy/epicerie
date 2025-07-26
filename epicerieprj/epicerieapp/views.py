from django.shortcuts import render, redirect


def home(request):
    return render(request, "epicerieapp/home.html")


def index(request):
    return render(request, "epicerieapp/index.html")


def applications_view(request):
    applications = [
        {"name": "App 1", "description": "Description of App 1"},
        {"name": "App 2", "description": "Description of App 2"},
        # Add more applications as needed
    ]
    return render(request, "epicerieapp/applications.html", {"applications": applications})


def about(request):
    return render(request, "epicerieapp/about.html")


def mission(request):
    return render(request, "epicerieapp/mission.html")


def vision(request):
    return render(request, "epicerieapp/vision.html")


def clientdataentry(request):
    return render(request, "epicerieapp/clientdataentry.html")


def contact(request):
    return render(request, "epicerieapp/contact.html")


def apps(request):
    return render(request, "epicerieapp/apps.html")


from django.shortcuts import render


# Existing views
def home(request):
    return render(request, "epicerieapp/home.html")


def index(request):
    return render(request, "epicerieapp/index.html")


# Add views for the new URLs
def attendance_view(request):
    return render(request, "epicerieapp/attendance.html")


def payroll_view(request):
    return render(request, "epicerieapp/payroll.html")


def tasks_management_view(request):
    return render(request, "epicerieapp/tasks_management.html")


def inventory_view(request):
    return render(request, "epicerieapp/inventory.html")


def online_grocery_view(request):
    return render(request, "epicerieapp/online_grocery.html")


def onlinetemp(request):
    return render(request, "epicerieapp/onlinetemp.html")
