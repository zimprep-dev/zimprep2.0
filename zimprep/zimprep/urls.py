"""
URL configuration for zimprep project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'), 
    path('dashboard/', views.dashboard, name='dashboard'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Note URLs
    path('notes/', views.NoteListView.as_view(), name='note-list'),
    path('notes/create/', views.NoteCreateView.as_view(), name='note-create'),
    path('notes/<int:pk>/', views.NoteDetailView.as_view(), name='note-detail'),
    path('notes/<int:pk>/edit/', views.NoteUpdateView.as_view(), name='note-update'),
    path('notes/<int:pk>/delete/', views.NoteDeleteView.as_view(), name='note-delete'),
    path('notes/quick-create/', views.note_quick_create, name='note-quick-create'),
    path('notes/<int:pk>/toggle-public/', views.note_toggle_public, name='note-toggle-public'),
    path('notes/<int:pk>/share/', views.note_share, name='note-share'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
