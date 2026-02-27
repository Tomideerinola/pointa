import datetime
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# Create your models here.


class Profile(models.Model):
    """
    Extends Django's built-in User model.
    This stores personal information that does NOT belong in auth.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    # One user → one profile
    # related_name="profile" lets us do: user.profile

    phone = models.CharField(max_length=20, blank=True)

    profile_pic = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True
    )
    # Django will auto-create the 'profiles/' folder inside MEDIA_ROOT

    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
    ]

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True
    )

    address = models.CharField(max_length=255, blank=True)

    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("suspended", "Suspended"),
    ]

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="active"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    

class Organizer(models.Model):
    """
    Organizer is a ROLE, not a separate login.
    Uses Django User for authentication.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="organizer"
    )
    # If a user has an Organizer record → they can create events

    organization_name = models.CharField(max_length=150)

    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)

    verified = models.BooleanField(default=False)

    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.organization_name


class Category(models.Model):
    """
    Event categories (Tech, Music, Conference, etc.)
    """

    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class State(models.Model):
    """
    Nigerian states (or any country states)
    """

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    


    


class Event(models.Model):
    """
    Events created by organizers
    """

    organizer = models.ForeignKey(
        Organizer,
        on_delete=models.CASCADE,
        related_name="events"
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name="events"
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    date = models.DateField()
    start_time = models.TimeField(default=datetime.time(9, 0))  # 09:00 AM
    end_time = models.TimeField(default=datetime.time(17, 0))  # 05:00 PM

    venue = models.CharField(max_length=255, blank=True)


    STATE_CHOICES = [
        ("lagos", "Lagos"),
        ("abuja", "Abuja (FCT)"),
    ]

    state = models.CharField(
        max_length=20,
        choices=STATE_CHOICES
    )

    city = models.CharField(max_length=100, blank=True)

    image = models.ImageField(
        upload_to="events/",
        blank=True,
        null=True
    )

    STATUS_CHOICES = [
        ("active", "Active"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="active"
    )
    EVENT_TYPE_CHOICES = [
    ("physical", "Physical Event"),
    ("online", "Online Event"),
    ("hybrid", "Hybrid Event"),
    ]

    event_type = models.CharField(
        max_length=10,
        choices=EVENT_TYPE_CHOICES,
        default="physical"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.state})"
    class Meta:
        ordering = ["-created_at"]




class Ticket(models.Model):
    """
    Ticket types for an event (VIP, Regular, Free)
    """

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_available = models.PositiveIntegerField()
    quantity_sold = models.PositiveIntegerField(default=0)  # ADD THIS

    def __str__(self):
        return f"{self.name} - {self.event.title}"



class Order(models.Model):
    """
    A payment order made by a user
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    reference = models.CharField(max_length=100, unique=True)
    # This will be used for Paystack reference

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    ]

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.reference


class OrderItem(models.Model):
    """
    Tickets inside an order
    """

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.ticket.name} x {self.quantity}"


class Attendee(models.Model):
    """
    Attendees registered for an event
    """

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="attendees"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="attendances"
    )

    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)

    tickets_qty = models.PositiveIntegerField(default=1)

    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("free", "Free"),
    ]

    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS_CHOICES,
        default="pending"
    )

    booking_ref = models.CharField(
        max_length=30,
        unique=True,
        null=True,
        blank=True
    )

    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.event.title}"



class SavedEvent(models.Model):

    # The user who saved the event
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE  # If user deletes account, saved events delete too
    )

    # The event that was saved
    event = models.ForeignKey(
        'Event',   # We use string reference to avoid circular import
        on_delete=models.CASCADE
    )

    # When the event was saved
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Prevent a user from saving the same event twice
        unique_together = ('user', 'event')

    def __str__(self):
        return f"{self.user.username} saved {self.event.title}"
    




class NewsletterEmail(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
    

class Payout(models.Model):
    """
    Stores payout requests made by organizers
    """

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('rejected', 'Rejected'),
    )

    organizer = models.ForeignKey(
        Organizer,
        on_delete=models.CASCADE,
        related_name='payouts'
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    reference = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.organizer.user.username} - {self.amount} - {self.status}"