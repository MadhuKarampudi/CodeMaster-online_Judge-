from django import forms
from .models import Problem, TestCase

class ProblemForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = ['title', 'description', 'difficulty', 'time_limit', 'memory_limit', 'constraints', 'function_name', 'parameters', 'return_type']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'constraints': forms.Textarea(attrs={'rows': 3}),
            'parameters': forms.Textarea(attrs={'rows': 3}),
        }

class TestCaseForm(forms.ModelForm):
    class Meta:
        model = TestCase
        fields = ['input_data', 'expected_output', 'is_sample']
        widgets = {
            'input_data': forms.Textarea(attrs={'rows': 3}),
            'expected_output': forms.Textarea(attrs={'rows': 3}),
        }