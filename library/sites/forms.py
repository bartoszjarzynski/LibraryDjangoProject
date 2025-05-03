from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class RegistrationForm(UserCreationForm):
    username = forms.CharField(
        max_length=35,
        widget=forms.TextInput(attrs={"placeholder": "Username"}),
    )
    email = forms.EmailField(
        max_length=150,
        widget=forms.EmailInput(attrs={"placeholder": "Email"}),
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Password"}),
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm Password"}),
    )
    role = forms.ChoiceField(
        choices=CustomUser.ROLE_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
        initial="reader"
    )

    class Meta:
        model = CustomUser
        fields = ["username", "email", "password1", "password2", "role"]
        help_texts = {
            "username": "",
            "email": "",
            "password1": "",
            "password2": "",
        }


class LoginForm(forms.Form):
    username = forms.CharField(max_length=35)
    password = forms.CharField(max_length=64)

    class Meta:
        fields = ["username", "password"]
        help_texts = {
            "username": "",
            "password": "",
        }
