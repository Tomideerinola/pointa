import uuid
import requests
from django.conf import settings
from django.db.models import Q
from django.utils.http import url_has_allowed_host_and_scheme
from django.http import JsonResponse
from django.utils import timezone
from django.urls import reverse
from django.db.models import Sum
from django.shortcuts import render, redirect , get_object_or_404
from .forms import UserRegisterForm, OrganizerRegisterForm, UserLoginForm, EventForm, OrganizerLoginForm,TicketFormSet,OrganizerForm,UserForm,UserUpdateForm
from django.contrib.auth import login as auth_login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Organizer, Profile, Event, Ticket, Order, Attendee, OrderItem, SavedEvent, Category
from django.contrib.auth.models import User

# Create your views here.


# homepage route 

def home(request):
    now = timezone.now()

    # Base queryset (only active events)
    events = Event.objects.filter(status="active")

    # Get category from URL
    category_id = request.GET.get('category')
    selected_category = None

    if category_id:
        events = events.filter(category_id=category_id)
        selected_category = Category.objects.filter(id=category_id).first()

    # Upcoming events (filtered if category selected)
    upcoming_events = events.filter(
        date__gte=now
    ).order_by('date')

    # Past events (filtered if category selected)
    past_events = events.filter(
        date__lt=now
    ).order_by('-date')

    categories = Category.objects.all()

    return render(request, 'events/index.html', {
        "upc": upcoming_events,
        "past": past_events,
        "categories": categories,
        "selected_category": selected_category,
    })

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


def user_login(request):

    form = UserLoginForm(request.POST or None)

    #Get next from POST first (after form submission), else GET
    next_url = request.POST.get("next") or request.GET.get("next")

    if request.method == "POST":

        if form.is_valid():

            user = form.cleaned_data["user"]

            auth_login(request, user)

            if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()}
            ):
                return redirect(next_url)

            return redirect("dashboard")

    return render(request, "events/login.html", {
        "form": form,
        "next": next_url
    })




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
@login_required
def dashboard(request):

    # Get current logged in user
    user = request.user

    # Get current time (used for filtering past/upcoming events)
    now = timezone.now()


    # Upcoming Events (based on date)

    upcoming_events = Event.objects.filter(
        date__gte=now  # Event date greater than or equal to now
    ).order_by('date')[:3]  # Show only 3 on dashboard


    # Past Events

    past_events = Event.objects.filter(
        date__lt=now
    ).order_by('-date')[:3]


    # Saved Events Count

    saved_count = SavedEvent.objects.filter(
        user=user
    ).count()

    context = {
        "user": user,
        "upcoming_events": upcoming_events,
        "past_events": past_events,
        "saved_count": saved_count,
    }

    return render(request, 'events/dashboard_home.html', context)


@login_required(login_url='organizer_login')
def create_event(request):
    try:
        organizer = request.user.organizer
    except Organizer.DoesNotExist:
        messages.error(request, "You must be an organizer to create events.")
        return redirect('org_dashboard')

    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        ticket_formset = TicketFormSet(request.POST)

        if form.is_valid() and ticket_formset.is_valid():
            # Save the event
            event = form.save(commit=False)
            event.organizer = organizer
            event.save()

            # Attach formset to event and save
            ticket_formset.instance = event
            ticket_formset.save()

            messages.success(request, f'Success! "{event.title}" has been created.')
            return redirect("my_events")

        else:
            # DEBUG: print errors to console
            print("Event Form Errors:", form.errors)            # Shows which fields are failing in the event form
            print("Ticket Formset Errors:", ticket_formset.errors)  # Shows which tickets are invalid

    else:
        form = EventForm()
        ticket_formset = TicketFormSet(queryset=Ticket.objects.none())

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

    # Start with active events
    events = Event.objects.filter(status="active")

    # Get filter values from URL
    q = request.GET.get("q")
    city = request.GET.get("city")
    category_id = request.GET.get("category")
    locations = request.GET.getlist("location")  # for checkboxes

    # 🔎 Search by name or category name
    if q:
        events = events.filter(
            Q(title__icontains=q) |
            Q(category__name__icontains=q)
        )

    # 📍 Filter by city input (top search bar)
    if city:
        events = events.filter(venue__icontains=city)

    # 📂 Filter by category (dropdown)
    if category_id:
        events = events.filter(category_id=category_id)

    # 📌 Filter by multiple checkbox locations
    if locations:
        events = events.filter(venue__in=locations)

    events = events.order_by("-date")

    categories = Category.objects.all()
    available_locations = ["Lagos", "Abuja"]

    return render(request, "events/events_list.html", {
        "events": events,
        "categories": categories,
        "selected_category": category_id,
        "selected_locations": locations,
        "q": q,
        "city": city,
        "available_locations": available_locations,
    })


def event_detail(request, event_id):
    """
    Show the details of a single event.
    """
    event = get_object_or_404(Event, id=event_id)
    tickets = event.tickets.all()  # Get all ticket types for this event
    # Check if this specific user has saved this event
    is_saved = False
    if request.user.is_authenticated:
        is_saved = SavedEvent.objects.filter(user=request.user, event=event).exists()
    context = {
        "event": event,
        "tickets": tickets,
        "is_saved": is_saved,
    }
    return render(request, "events/event_detail.html", context)


@login_required
def toggle_save_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    saved_item = SavedEvent.objects.filter(user=request.user, event=event)

    if saved_item.exists():
        saved_item.delete()
        saved = False
    else:
        SavedEvent.objects.create(user=request.user, event=event)
        saved = True

    return JsonResponse({'saved': saved})


def booking_confirm(request, event_id):
    """
    Handles ticket selection and shows confirmation page
    Requires user to be logged in
    """
        # Manual authentication check instead of using login required 
    if not request.user.is_authenticated:
        messages.warning(
            request,
            "You need to login before booking an event."
        )

        # Get login URL dynamically
        login_url = reverse("user_login")
                # Redirect to login with next parameter
        return redirect(f"{login_url}?next={request.path}")


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

def my_events(request):
        try:
            org = request.user.organizer
        except Organizer.DoesNotExist:
            return redirect('organizer_login')
    
        events = Event.objects.filter(organizer=org)


        for event in events:

            # ✅ Total tickets available
            total_tickets = Ticket.objects.filter(
                event=event
            ).aggregate(total=Sum('quantity_available'))

            event.total_tickets = total_tickets['total'] or 0


            # ✅ Tickets sold
            sold = OrderItem.objects.filter(
                order__event=event,
                order__status="paid"
            ).aggregate(total=Sum('quantity'))

            event.tickets_sold = sold['total'] or 0


            # ✅ Percentage
            if event.total_tickets > 0:
                event.sold_percentage = int(
                    (event.tickets_sold / event.total_tickets) * 100
                )
            else:
                event.sold_percentage = 0

        return render(request, 'events/my_events.html', {"events":events, "now": timezone.now()})




def edit_event(request, pk):
    try:
        org = request.user.organizer
    except Organizer.DoesNotExist:
        return redirect('organizer_login')

    event = get_object_or_404(Event, pk=pk, organizer=org)

    if request.method == "POST":
        form = EventForm(request.POST, request.FILES, instance=event)
        ticket_formset = TicketFormSet(request.POST, instance=event)

        if form.is_valid() and ticket_formset.is_valid():
            form.save()
            ticket_formset.save()
            messages.success(request, "Event updated successfully.")
            return redirect("my_events")

    else:
        form = EventForm(instance=event)
        ticket_formset = TicketFormSet(instance=event)

    return render(request, "events/edit_event.html", {
        "form": form,
        "ticket_formset": ticket_formset
    })


def delete_event(request, pk):

    try:
        org = request.user.organizer
    except Organizer.DoesNotExist:
        return redirect('organizer_login')

    event = get_object_or_404(
        Event,
        pk=pk,
        organizer=org
    )

    if request.method == "POST":
        event.delete()
        messages.success(request, "Event deleted successfully.")
        return redirect('my_events')

    return redirect('my_events')

@login_required(login_url='organizer_login')
def organizer_profile(request):
    try:
        org = request.user.organizer  # Try to get the organizer record
    except Organizer.DoesNotExist:
        messages.error(request, "You are not registered as an organizer.")
        return redirect('org_dashboard')  # Or wherever makes sense

    if request.method == "POST":
        org_form = OrganizerForm(request.POST, instance=org)
        user_form = UserForm(request.POST, instance=request.user)

        if org_form.is_valid() and user_form.is_valid():
            org_form.save()
            user_form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('organizer_profile')
    else:
        org_form = OrganizerForm(instance=org)
        user_form = UserForm(instance=request.user)

    return render(request, 'events/organizer_profile.html', {
        'org_form': org_form,
        'user_form': user_form
    })

@login_required(login_url='organizer_login')
def organizer_tickets(request):
    try:
        organizer = request.user.organizer
    except Organizer.DoesNotExist:
        return redirect('organizer_login')

    events = Event.objects.filter(
        organizer=organizer
    ).prefetch_related('tickets')  # ← use your related_name here

    total_tiers = 0
    total_stock = 0

    for event in events:
        tiers = event.tickets.all()  # ← use related_name
        total_tiers += tiers.count()
        total_stock += sum(t.quantity_available for t in tiers)

    context = {
        "events": events,
        "total_tiers": total_tiers,
        "total_stock": total_stock,
    }

    return render(request, "events/organizer_tickets.html", context)




def payout(request):
    return render(request,'events/payouts.html')



@login_required
def upcoming_events(request):

    now = timezone.now()

    events = Event.objects.filter(
        date__gte=now
    ).order_by('date')

    return render(request, 'events/upcoming_events.html', {
        "events": events
    })


@login_required
def my_tickets(request):
    """
    Shows all PAID ticket orders for the logged-in user
    """

    # Get all paid orders for this user
    # select_related("event") → Optimizes query by joining Event table
    # prefetch_related("items__ticket") → Loads ticket data efficiently
    orders = (
        Order.objects
        .filter(user=request.user, status="paid")
        .select_related("event")
        .prefetch_related("items__ticket")
        .order_by("-created_at")
    )

    context = {
        "orders": orders,
        "today": timezone.now().date(),  # Used to check past/upcoming
    }

    return render(request, "events/my_tickets.html", context)

@login_required
def past_events(request):

    now = timezone.now()

    events = Event.objects.filter(
        date__lt=now
    ).order_by('-date')

    return render(request, 'events/past_events.html', {
        "events": events
    })


@login_required
def saved_events(request):

    user = request.user

    saved = SavedEvent.objects.filter(
        user=user
    ).select_related('event')

    return render(request, 'events/saved_events.html', {
        "saved_events": saved
    })


@login_required
def edit_profile(request):
    """
    Allows logged-in users to update their profile
    """

    # If user submits form (POST request)
    if request.method == "POST":

        # Bind submitted data to form
        form = UserUpdateForm(request.POST, instance=request.user)

        # Check if form data is valid
        if form.is_valid():

            # Save the updated user info
            form.save()

            # Show success message
            messages.success(request, "Profile updated successfully!")

            # Redirect back to dashboard
            return redirect("dashboard")

    else:
        # If page is loaded normally (GET request),
        # pre-fill form with existing user data
        form = UserUpdateForm(instance=request.user)

    return render(request, "events/edit_profile.html", {
        "form": form
    })