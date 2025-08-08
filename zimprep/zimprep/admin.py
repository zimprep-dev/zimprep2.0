from django.contrib import admin
from .models import Note

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'subject', 'is_public', 'created_date', 'updated_date')
    list_filter = ('subject', 'is_public', 'created_date', 'user')
    search_fields = ('title', 'content', 'tags', 'user__username')
    readonly_fields = ('created_date', 'updated_date')
    date_hierarchy = 'created_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'content', 'subject')
        }),
        ('User & Privacy', {
            'fields': ('user', 'is_public')
        }),
        ('Additional Information', {
            'fields': ('tags', 'attachment'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_date', 'updated_date'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Show all notes in admin"""
        return super().get_queryset(request)
    
    def save_model(self, request, obj, form, change):
        """Set user if not already set"""
        if not change:  # Only for new notes
            obj.user = request.user
        super().save_model(request, obj, form, change)
