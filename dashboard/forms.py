from django import forms
from django.urls import reverse
from .models import Data
from django.contrib.auth.views import LoginView

class DataForm(forms.ModelForm):
    class Meta:
        model = Data
        fields = ['country', 'population']
        widgets = {
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'population': forms.NumberInput(attrs={'class': 'form-control'})
        }
        # forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
class CustomLoginView(LoginView):
    template_name = 'dashboard/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse('dashboard:dashboard')  # Redirect to dashboard after login
