from django import forms
from .models import Profile, Organizer
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from django.contrib.auth.models import User


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