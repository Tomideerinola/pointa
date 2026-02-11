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
    class Meta:
        model = Organizer
        fields = ("organization_name", "email", "phone")


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