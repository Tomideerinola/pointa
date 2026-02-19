from django import forms
from .models import Profile, Organizer, Event, Ticket
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta


class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name','username' ,'email', 'password1', 'password2']

    

    def __init__(self, *args, **kwargs):
        # This method runs every time the form is created
        super().__init__(*args, **kwargs)

        # FIRST NAME FIELD STYLING
        self.fields["first_name"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "John",
        })

        # LAST NAME FIELD STYLING
        self.fields["last_name"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Doe",
        })
        
        # username field 

        self.fields["username"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Choose your Username",
        })

        # EMAIL FIELD STYLING
        self.fields["email"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "john@example.com",
        })

        # PASSWORD 1 STYLING
        self.fields["password1"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Create a password",
        })

        # PASSWORD 2 STYLING
        self.fields["password2"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Confirm your password",
        })


class OrganizerRegisterForm(forms.ModelForm):
    # Add password and confirm password fields
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Secure password"
        }),
        label="Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirm password"
        }),
        label="Confirm Password"
    )

    class Meta:
        model = Organizer
        fields = ["organization_name", "email", "phone"]

    def __init__(self, *args, **kwargs):
            """
            Style the form fields to match your template design
            """
            super().__init__(*args, **kwargs)

            # ORGANIZATION/BUSINESS NAME
            self.fields["organization_name"].widget.attrs.update({
                "class": "form-control",
                "placeholder": "e.g. Lagos Fun Events"
            })

            # EMAIL
            self.fields["email"].widget.attrs.update({
                "class": "form-control",
                "placeholder": "contact@business.com"
            })

            # PHONE
            self.fields["phone"].widget.attrs.update({
                "class": "form-control",
                "placeholder": "e.g. +234 801 234 5678"
            })


    def clean(self):
        """
        Ensure password and confirm_password match
        """
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")

        if password != confirm:
            raise forms.ValidationError("Passwords do not match")

        # Check if email already exists in User table
        email = cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists")

        return cleaned_data

    def save(self, commit=True):
        """
        Create Django User first, then Organizer linked to it
        """
        # Create User object
        user = User.objects.create_user(
            username=self.cleaned_data["email"],  # use email as username
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"]
        )

        # Create Organizer object
        organizer = Organizer.objects.create(
            user=user,
            organization_name=self.cleaned_data["organization_name"],
            phone=self.cleaned_data.get("phone", "")
        )

        return organizer


class UserLoginForm(forms.Form):
    """
    Custom login form using email instead of username
    """
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "name@example.com",
        }),
        label="Email Address"
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "••••••••",
        }),
        label="Password"
    )

    def clean(self):
        """
        Authenticate user based on email and password
        """
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            try:
                # Get user by email
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise forms.ValidationError("Invalid email or password.")

            # Check password
            if not user.check_password(password):
                raise forms.ValidationError("Invalid email or password.")

            # Attach user object to form for easy login in view
            cleaned_data["user"] = user

        return cleaned_data
    






class EventForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = "Select Category"
        self.fields['state'].empty_label = "Select State"

    class Meta:
        model = Event
        fields = [
            "title",
            "category",
            "event_type",
            "description",
            "venue",
            "date",
            "state",
            "city",
            "image",
            "start_time",
            "end_time",
        ]
        widgets = {

            # Text input
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. Lagos Jazz Night 2026"
            }),

            # Dropdown (Category)
            "category": forms.Select(attrs={
                "class": "form-select"
            }),

            # Dropdown (Event Type)
            "event_type": forms.Select(attrs={
                "class": "form-select"
            }),

            # Textarea
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Tell your audience what to expect..."
            }),

            # Venue
            "venue": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. Eko Hotels & Suites, VI"
            }),

            # Date
            "date": forms.DateInput(attrs={
                "type": "date",
                "class": "form-control"
            }),

            # State dropdown
            "state": forms.Select(attrs={
                "class": "form-select"
            }),
            "city": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. Lekki, Yaba, Garki"
            }),
            # Image upload
            "image": forms.FileInput(attrs={
                "class": "form-control"
            }),
            # Start Time
            "start_time": forms.TimeInput(attrs={
                "type": "time",
                "class": "form-control"
            }),
            # End Time
            "end_time": forms.TimeInput(attrs={
                "type": "time",
                "class": "form-control"
            }),
        }

    # 🔥 MOVE THESE OUTSIDE META
    def clean_date(self):
        date = self.cleaned_data.get("date")
        if date < timezone.now().date():
            raise ValidationError("Event date cannot be in the past.")
        return date

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        if start_time and end_time:
            if end_time <= start_time:
                raise ValidationError("End time must be after start time.")

        return cleaned_data








class TicketForm(forms.ModelForm):
    """
    Form for creating ticket types
    """

    class Meta:
        model = Ticket
        fields = ["name", "price", "quantity_available"]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. Regular Access"
            }),
            "price": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "0.00",
                "min": "0"
            }),
            "quantity_available": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "100",
                "min": "1"
            }),

        }


class OrganizerLoginForm(forms.Form):
    """
    Login form for organizers.
    We use a normal Form (not ModelForm) because
    we are not creating a model instance.
    """

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "organizer@pointa.com"
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "••••••••"
        })
    )

    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            "class": "form-check-input"
        })
    )

    def clean(self):
        """
        This method validates the email & password.
        """
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            try:
                # Find user by email
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise forms.ValidationError("Invalid email or password.")

            # Authenticate using username + password
            user = authenticate(
                username=user.username,
                password=password

            )

            if user is None:
                raise forms.ValidationError("Invalid email or password.")

            cleaned_data["user"] = user

        return cleaned_data
    


TicketFormSet = inlineformset_factory(
    Event,
    Ticket,
    form=TicketForm,
    extra=1,          # show at least 1 empty ticket form
    can_delete=True
)


class OrganizerForm(forms.ModelForm):

    class Meta:
        model = Organizer
        fields = [
            "organization_name",
            "email",
            "phone",
            "bio",
        ]


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["email"]  # This is the login email