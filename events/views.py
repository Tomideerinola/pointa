from django.shortcuts import render, redirect , get_object_or_404
from .forms import UserRegisterForm, OrganizerRegisterForm, UserLoginForm, EventForm, OrganizerLoginForm,TicketFormSet
from django.contrib.auth import login as auth_login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Organizer, Profile, Event
from django.contrib.auth.models import User

# Create your views here.


# homepage route 

def home(request):
    events = Event.objects.filter(status="active").order_by("-date")  # show upcoming first
    return render(request, 'events/index.html', {'events':events})

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


@login_required (login_url='organizer_login')
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


def organizer_logout(request):
    logout(request)
    return redirect("organizer_login")



# user dashboard view 
def dashboard(request):
    user = request.user
    context = {"user":user}
    return render(request, 'events/user_dashboard.html', context)



@login_required(login_url='organizer_login')
def create_event(request):

    organizer = request.user.organizer

    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        ticket_formset = TicketFormSet(request.POST)

        if form.is_valid() and ticket_formset.is_valid():

            event = form.save(commit=False)
            event.organizer = organizer
            event.save()

            tickets = ticket_formset.save(commit=False)
            for ticket in tickets:
                ticket.event = event
                ticket.save()
            messages.success(request, f'Success! "{event.title}" has been created.')

            return redirect("org_dashboard")

    else:
        form = EventForm()
        ticket_formset = TicketFormSet()

    return render(request, "events/create_event.html", {
        "form": form,
        "ticket_formset": ticket_formset
    })


def organizer_login(request):
    """
    Login view for organizers.
    """

    if request.method == "POST":
        form = OrganizerLoginForm(request.POST)

        if form.is_valid():
            user = form.cleaned_data["user"]

            # Log the user in
            auth_login(request, user)

            # Handle remember me
            if not form.cleaned_data.get("remember_me"):
                request.session.set_expiry(0)  # expires when browser closes

            return redirect("org_dashboard")

    else:
        form = OrganizerLoginForm()

    return render(request, "events/org_login.html", {"form": form})


def events_list(request):
    events = Event.objects.filter(status="active").order_by("-date")  # show upcoming first
    return render(request, "events/events_list.html", {"events": events})


def event_detail(request, event_id):
    """
    Show the details of a single event.
    """
    event = get_object_or_404(Event, id=event_id)
    tickets = event.tickets.all()  # Get all ticket types for this event
    context = {
        "event": event,
        "tickets": tickets,
    }
    return render(request, "events/event_detail.html", context)

