from django.shortcuts import render, redirect

def home(request):
    return render(request, 'homeapp/home.html')

def applications_view(request):
    applications = [
        {'name': 'App 1', 'description': 'Description of App 1'},
        {'name': 'App 2', 'description': 'Description of App 2'},
        # Add more applications as needed
    ]
    return render(request, 'homeapp/applications.html', {'applications': applications})