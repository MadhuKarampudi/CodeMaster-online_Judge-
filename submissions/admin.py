from django.contrib import admin
from .models import Submission


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'problem', 'language', 'status', 'submitted_at', 'execution_time']
    list_filter = ['status', 'language', 'submitted_at', 'problem']
    search_fields = ['user__username', 'problem__title']
    readonly_fields = ['submitted_at', 'execution_time', 'memory_used']
    
    fieldsets = (
        ('Submission Info', {
            'fields': ('user', 'problem', 'language', 'submitted_at')
        }),
        ('Code', {
            'fields': ('code',),
            'classes': ('collapse',)
        }),
        ('Results', {
            'fields': ('status', 'output', 'error', 'execution_time', 'memory_used')
        }),
    )
    
    def has_add_permission(self, request):
        # Prevent adding submissions through admin
        return False

