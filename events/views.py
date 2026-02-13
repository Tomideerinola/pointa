from django.shortcuts import render, redirect , get_object_or_404
from .forms import UserRegisterForm, OrganizerRegisterForm, UserLoginForm, EventForm
from django.contrib.auth import login as auth_login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .models import Organizer, Profile
from django.contrib.auth.models import User

# Create your views here.


# homepage route 

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

# user logout 

def user_logout(request):
    """
    Logs out the current user and redirects to home page
    """
    logout(request)  # Clear the session
    return redirect('home')  # Redirect to homepage (or login)


# user login view 
def user_login(request):
    """
    Handle login with email and password
    """
    form = UserLoginForm(request.POST or None)  # instantiate with POST data if available

    if request.method == "POST":
        if form.is_valid():
            # Get the authenticated user from cleaned_data
            user = form.cleaned_data["user"]

            # Log the user in
            auth_login(request, user)

            # Redirect to dashboard
            return redirect("dashboard")

    # Always pass the form to the template, even if GET or invalid POST
    return render(request, "events/login.html", {"form": form, "DEBUG_VIEW": "THIS IS USER_LOGIN VIEW"})




def organizer_signup(request):
    """
    Signup view for organizers
    """
    if request.method == "POST":
        form = OrganizerRegisterForm(request.POST)
        if form.is_valid():
            organizer = form.save()  # Creates both User and Organizer
            auth_login(request, organizer.user)  # log in the user automatically
            return redirect("org_dashboard")  # redirect to organizer dashboard
    else:
        form = OrganizerRegisterForm()

    return render(request, "events/org_signup.html", {"form": form})



def org_signup(request):
    return render(request, 'events/org_signup.html')

def login(request):
    return render(request, 'events/login.html')


# user dashboard view 
def dashboard(request):
    user = request.user
    context = {"user":user}
    return render(request, 'events/user_dashboard.html', context)


@login_required
def org_dashboard(request):
    """
    Organizer dashboard view.
    Only accessible to logged-in users.
    """
    # Get the organizer profile of the logged-in user
    try:
        org = request.user.organizer  # this works because of the related_name='organizer'
    except Organizer.DoesNotExist:
        # Optional: handle case where logged-in user is not an organizer
        org = None

    context = {'organizer': org}
    return render(request, 'events/org_dashboard.html', context)


def create_event(request):
    """
    Allows an organizer to create an event
    """

    organizer = request.user.organizer

    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)

        if form.is_valid():
            event = form.save(commit=False)

            # Attach logged in organizer
            event.organizer = organizer

            event.save()

            return redirect("org_dashboard")

    else:
        form = EventForm()

    return render(request, "events/create_event.html", {"form": form})
