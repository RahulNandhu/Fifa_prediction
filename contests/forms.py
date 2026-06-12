from django import forms

from .models import ContestGroup


class ContestGroupForm(forms.ModelForm):
    class Meta:
        model = ContestGroup
        fields = ['name', 'description', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
