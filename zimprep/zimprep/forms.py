from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomerUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

class Meta:
    model = User
    fields = ("email", "password")

def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes to form fields to match your styling
        # REPLACE 'your-input-class' with your actual CSS class names
        self.fields['email'].widget.attrs.update({'class': 'form-group input'})
        self.fields['password'].widget.attrs.update({'class': 'form-group input'})
    

def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
