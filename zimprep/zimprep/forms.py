from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Note, SUBJECT_CHOICES

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

# Note Forms
class NoteForm(forms.ModelForm):
    """Form for creating and editing notes"""
    
    class Meta:
        model = Note
        fields = ['title', 'content', 'subject', 'attachment', 'tags', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter note title',
                'maxlength': '200'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Enter your note content here...',
                'style': 'resize: vertical;'
            }),
            'subject': forms.Select(attrs={
                'class': 'form-control'
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter tags separated by commas (e.g., math, algebra, formulas)'
            }),
            'attachment': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.txt,.jpg,.jpeg,.png'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def clean_title(self):
        """Validate title length and uniqueness"""
        title = self.cleaned_data.get('title')
        if len(title.strip()) < 3:
            raise forms.ValidationError("Title must be at least 3 characters long.")
        return title.strip()
    
    def clean_content(self):
        """Validate content is not empty"""
        content = self.cleaned_data.get('content')
        if len(content.strip()) < 10:
            raise forms.ValidationError("Note content must be at least 10 characters long.")
        return content.strip()
    
    def clean_attachment(self):
        """Validate file size and type"""
        attachment = self.cleaned_data.get('attachment')
        if attachment:
            # Check file size (5MB limit)
            if attachment.size > 5 * 1024 * 1024:
                raise forms.ValidationError("File size must be under 5MB.")
            
            # Check file extension
            allowed_extensions = ['.pdf', '.doc', '.docx', '.txt', '.jpg', '.jpeg', '.png']
            file_extension = attachment.name.lower()
            if not any(file_extension.endswith(ext) for ext in allowed_extensions):
                raise forms.ValidationError("Only PDF, DOC, DOCX, TXT, JPG, JPEG, and PNG files are allowed.")
        
        return attachment

class NoteSearchForm(forms.Form):
    """Form for searching notes"""
    
    SEARCH_CHOICES = [
        ('title', 'Title'),
        ('content', 'Content'),
        ('subject', 'Subject'),
        ('tags', 'Tags'),
        ('all', 'All Fields'),
    ]
    
    query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search notes...',
            'aria-label': 'Search notes'
        })
    )
    
    search_in = forms.ChoiceField(
        choices=SEARCH_CHOICES,
        initial='all',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    subject_filter = forms.ChoiceField(
        choices=[('', 'All Subjects')] + SUBJECT_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    public_only = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

class NoteQuickForm(forms.ModelForm):
    """Simplified form for quick note creation"""
    
    class Meta:
        model = Note
        fields = ['title', 'content', 'subject']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Quick note title'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Write your quick note here...'
            }),
            'subject': forms.Select(attrs={
                'class': 'form-control'
            })
        }
