from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .forms import CustomerUserCreationForm, NoteForm, NoteSearchForm, NoteQuickForm
from .models import Note

# from django.template import loader

def home(request):
    # template = loader.get_template('base.html')
    return render(request, 'landing/base.html')

@login_required
def dashboard(request):
    return render(request, 'authed-user/dashboard.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'landing/login-page.html', {'form': form})

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomerUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                messages.success(request, f'Account created successfully! Welcome, {user.username}!')
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}')
        else:
            # Display specific form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CustomerUserCreationForm()
    
    return render(request, 'landing/signup_page.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

# Legacy view for backward compatibility
def login(request):
    return login_view(request)

# Note Views
class NoteListView(LoginRequiredMixin, ListView):
    """Display all notes for the current user"""
    model = Note
    template_name = 'authed-user/notes/note_list.html'
    context_object_name = 'notes'
    paginate_by = 10
    
    def get_queryset(self):
        """Filter notes by user and search parameters"""
        queryset = Note.objects.filter(user=self.request.user)
        
        # Handle search
        search_form = NoteSearchForm(self.request.GET)
        if search_form.is_valid():
            query = search_form.cleaned_data.get('query')
            search_in = search_form.cleaned_data.get('search_in')
            subject_filter = search_form.cleaned_data.get('subject_filter')
            date_from = search_form.cleaned_data.get('date_from')
            date_to = search_form.cleaned_data.get('date_to')
            
            if query:
                if search_in == 'all':
                    queryset = queryset.filter(
                        Q(title__icontains=query) |
                        Q(content__icontains=query) |
                        Q(tags__icontains=query)
                    )
                elif search_in == 'title':
                    queryset = queryset.filter(title__icontains=query)
                elif search_in == 'content':
                    queryset = queryset.filter(content__icontains=query)
                elif search_in == 'subject':
                    queryset = queryset.filter(subject__icontains=query)
                elif search_in == 'tags':
                    queryset = queryset.filter(tags__icontains=query)
            
            if subject_filter:
                queryset = queryset.filter(subject=subject_filter)
            
            if date_from:
                queryset = queryset.filter(created_date__gte=date_from)
            
            if date_to:
                queryset = queryset.filter(created_date__lte=date_to)
        
        return queryset.order_by('-created_date')
    
    def get_context_data(self, **kwargs):
        """Add search form to context"""
        context = super().get_context_data(**kwargs)
        context['search_form'] = NoteSearchForm(self.request.GET)
        context['quick_form'] = NoteQuickForm()
        return context

class NoteDetailView(LoginRequiredMixin, DetailView):
    """Display a single note"""
    model = Note
    template_name = 'authed-user/notes/note_detail.html'
    context_object_name = 'note'
    
    def get_queryset(self):
        """Only show notes owned by the user or public notes"""
        return Note.objects.filter(
            Q(user=self.request.user) | Q(is_public=True)
        )

class NoteCreateView(LoginRequiredMixin, CreateView):
    """Create a new note"""
    model = Note
    form_class = NoteForm
    template_name = 'authed-user/notes/note_form.html'
    success_url = reverse_lazy('note-list')
    
    def form_valid(self, form):
        """Set the user before saving"""
        form.instance.user = self.request.user
        messages.success(self.request, 'Note created successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Handle form errors"""
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)

class NoteUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update an existing note"""
    model = Note
    form_class = NoteForm
    template_name = 'authed-user/notes/note_form.html'
    success_url = reverse_lazy('note-list')
    
    def test_func(self):
        """Check if user owns the note"""
        note = self.get_object()
        return note.user == self.request.user
    
    def form_valid(self, form):
        """Handle successful form submission"""
        messages.success(self.request, 'Note updated successfully!')
        return super().form_valid(form)

class NoteDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a note"""
    model = Note
    template_name = 'authed-user/notes/note_confirm_delete.html'
    success_url = reverse_lazy('note-list')
    
    def test_func(self):
        """Check if user owns the note"""
        note = self.get_object()
        return note.user == self.request.user
    
    def delete(self, request, *args, **kwargs):
        """Handle successful deletion"""
        messages.success(request, 'Note deleted successfully!')
        return super().delete(request, *args, **kwargs)

# Function-based views for AJAX operations
@login_required
def note_quick_create(request):
    """Quick note creation via AJAX"""
    if request.method == 'POST':
        form = NoteQuickForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.save()
            return JsonResponse({
                'success': True,
                'message': 'Note created successfully!',
                'note_id': note.id,
                'note_title': note.title
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
def note_toggle_public(request, pk):
    """Toggle note public/private status"""
    note = get_object_or_404(Note, pk=pk, user=request.user)
    note.is_public = not note.is_public
    note.save()
    
    status = 'public' if note.is_public else 'private'
    messages.success(request, f'Note is now {status}.')
    
    return JsonResponse({
        'success': True,
        'is_public': note.is_public,
        'message': f'Note is now {status}.'
    })

@login_required
def note_share(request, pk):
    """Share a note (placeholder for future implementation)"""
    note = get_object_or_404(Note, pk=pk, user=request.user)
    # This would typically generate a shareable link or send via email
    messages.info(request, 'Share functionality coming soon!')
    return redirect('note-detail', pk=pk)

