from django.shortcuts import render, redirect , get_object_or_404
from .forms import UserRegisterForm, OrganizerRegisterForm
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.decorators import login_required
from .models import Organizer, Profile

# Create your views here.

def home(request):
    return render(request, 'events/index.html')

def user_signup(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user= form.save()
            auth_login(request,user)
            return redirect('dashboard')
    else:
            form = UserRegisterForm()
    return render(request, 'events/user_signup.html', {'form':form})

def org_signup(request):
    return render(request, 'events/org_signup.html')

def login(request):
    return render(request, 'events/login.html')

def dashboard(request):
    user = request.user
    context = {"user":user}
    return render(request, 'events/dashboard.html', context)
