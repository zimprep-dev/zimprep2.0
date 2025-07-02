from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomerUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes to form fields to match your styling
        self.fields['username'].widget.attrs.update({'class': 'form-group input', 'placeholder': 'Enter your username'})
        self.fields['email'].widget.attrs.update({'class': 'form-group input', 'placeholder': 'Enter your email'})
        self.fields['password1'].widget.attrs.update({'class': 'form-group input', 'placeholder': 'Create a password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-group input', 'placeholder': 'Confirm your password'})
        
        # Update labels
        self.fields['username'].label = 'Username'
        self.fields['email'].label = 'Email address'
        self.fields['password1'].label = 'Password'
        self.fields['password2'].label = 'Confirm Password'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
