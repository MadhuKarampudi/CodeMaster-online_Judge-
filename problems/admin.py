from django.contrib import admin
from .models import Problem, TestCase

class TestCaseInline(admin.TabularInline):
    model = TestCase
    extra = 1

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    # Removed 'created_at' from the list_display and list_filter
    list_display = ('title', 'difficulty', 'time_limit', 'memory_limit', 'function_name')
    list_filter = ('difficulty',)
    search_fields = ('title', 'description')
    inlines = [TestCaseInline]
    
    # Optional: Make the new template fields easier to edit
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'difficulty')
        }),
        ('Execution Details', {
            'fields': ('time_limit', 'memory_limit', 'constraints')
        }),
        ('Function Signature', {
            'classes': ('collapse',),
            'fields': ('function_name', 'parameters', 'return_type')
        }),
    )

@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ('problem', 'is_sample')
    list_filter = ('problem', 'is_sample')