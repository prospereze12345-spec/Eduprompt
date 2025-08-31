from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from .models import Profile


class RegisterForm(UserCreationForm):
    full_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    number = forms.CharField(max_length=20, required=True)
    country = forms.CharField(max_length=100, required=False)

    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email'].lower()  # ensure unique username
        user.email = self.cleaned_data['email'].lower()

        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                full_name=self.cleaned_data['full_name'],
                number=self.cleaned_data['number'],
                country=self.cleaned_data.get('country', '')
            )
        return user







class LoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))



class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')