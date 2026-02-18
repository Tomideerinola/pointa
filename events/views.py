import uuid
import requests
from django.conf import settings
from django.urls import reverse
from django.shortcuts import render, redirect , get_object_or_404
from .forms import UserRegisterForm, OrganizerRegisterForm, UserLoginForm, EventForm, OrganizerLoginForm,TicketFormSet
from django.contrib.auth import login as auth_login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Organizer, Profile, Event, Ticket, Order, Attendee, OrderItem
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


@login_required(login_url='organizer_login')
def org_dashboard(request):
    """
    Organizer dashboard view.
    Shows stats: total events, total attendees, total revenue, and recent registrations
    """
    try:
        org = request.user.organizer
    except Organizer.DoesNotExist:
        return redirect('organizer_login')  # redirect if user is not an organizer

    # All events by this organizer
    events = Event.objects.filter(organizer=org)

    # All orders for these events
    orders = Order.objects.filter(event__in=events).order_by('-created_at')  # latest first

    # Dashboard stats
    total_events = events.count()
    total_attendees = orders.count()
    total_revenue = sum(order.total_amount for order in orders if order.status == 'paid')
    total_paid_orders = Order.objects.filter(
        event__in=events,
        status="paid"
    ).count()

    context = {
        'organizer': org,
        'events': events,
        'orders': orders,
        'total_events': total_events,
        'total_attendees': total_attendees,
        'total_revenue': total_revenue,
        'total_paid_orders': total_paid_orders,
    }
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

@login_required(login_url='user_login')
def booking_confirm(request, event_id):
    """
    Handles ticket selection and shows confirmation page
    Requires user to be logged in
    """

    event = get_object_or_404(Event, id=event_id)

    if request.method == "POST":
        ticket_id = request.POST.get("ticket_id")
        quantity = int(request.POST.get("quantity", 1))

        ticket = get_object_or_404(Ticket, id=ticket_id, event=event)

        # Validate quantity
        if quantity < 1:
            messages.error(request, "Invalid ticket quantity.")
            return redirect("event_detail", event_id=event.id)

        if quantity > ticket.quantity_available:
            messages.error(request, "Not enough tickets available.")
            return redirect("event_detail", event_id=event.id)

        total_amount = ticket.price * quantity

        # 🔥 Check if user already has a pending order for this event
        existing_order = Order.objects.filter(
            user=request.user,
            event=event,
            status="pending"
        ).first()

        if existing_order:
            # Clear previous items (avoid duplicates)
            existing_order.items.all().delete()
            order = existing_order
            order.total_amount = total_amount
            order.save()
        else:
            order = Order.objects.create(
                user=request.user,
                event=event,
                total_amount=total_amount,
                status="pending"
            )

        # Create OrderItem
        OrderItem.objects.create(
            order=order,
            ticket=ticket,
            quantity=quantity
        )

        context = {
            "event": event,
            "ticket": ticket,
            "quantity": quantity,
            "total_amount": total_amount,
            "order": order,  
        }

        return render(request, "events/booking_confirm.html", context)

    return redirect("event_detail", event_id=event.id)


@login_required
def initialize_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # generate unique reference
    reference = str(uuid.uuid4())
    order.reference = reference
    order.status = "pending"
    order.save()

    url = "https://api.paystack.co/transaction/initialize"

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "email": request.user.email,
        "amount": int(order.total_amount * 100),  # kobo
        "reference": reference,
        "callback_url": request.build_absolute_uri("/verify-payment/"),
    }

    response = requests.post(url, json=data, headers=headers)
    response_data = response.json()

    if response_data["status"]:
        return redirect(response_data["data"]["authorization_url"])
    else:
        messages.error(request, "Unable to initialize payment.")
        return redirect("booking_confirmation")
    


@login_required
def verify_payment(request):
    reference = request.GET.get("reference")

    url = f"https://api.paystack.co/transaction/verify/{reference}"

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }

    response = requests.get(url, headers=headers)
    response_data = response.json()

    if response_data["status"] and response_data["data"]["status"] == "success":

        order = Order.objects.get(reference=reference)

        if order.status != "paid":
            order.status = "paid"
            order.save()

            # Create attendees
            for item in order.items.all():
                Attendee.objects.create(
                    event=order.event,
                    user=order.user,
                    full_name=order.user.get_full_name(),
                    email=order.user.email,
                    tickets_qty=item.quantity,
                    payment_status="paid",
                    booking_ref=reference
                )

                # Reduce ticket quantity
                ticket = item.ticket
                ticket.quantity_available -= item.quantity
                ticket.save()

        return redirect(reverse("payment_success") + f"?reference={reference}")

    else:
        order = Order.objects.get(reference=reference)
        order.status = "failed"
        order.save()

        return redirect("payment_failed")
    

def payment_success(request):
    reference = request.GET.get("reference")
    order = Order.objects.filter(reference=reference).first()

    context = {
        "order": order
    }
    return render(request, "events/success.html", context)


def payment_failed(request):
    return render(request, "events/failed.html")



