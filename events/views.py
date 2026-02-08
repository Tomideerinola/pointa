from django.shortcuts import render, redirect , get_object_or_404

# Create your views here.

def home(request):
    return render(request, 'events/index.html')

def user_signup(request):
    return render(request, 'events/user_signup.html')

def org_signup(request):
    return render(request, 'events/org_signup.html')

def login(request):
    return render(request, 'events/login.html')
