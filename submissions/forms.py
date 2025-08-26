from django import forms
from .models import Submission


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['code', 'language']
        widgets = {
            'code': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 20,
                'placeholder': 'Write your code here...',
                'style': 'font-family: monospace;'
            }),
            'language': forms.Select(attrs={
                'class': 'form-control'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['language'].empty_label = 'Select Language'

