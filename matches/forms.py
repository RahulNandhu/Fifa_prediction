from django import forms

from .models import Fixture, Match


class FixtureForm(forms.ModelForm):
    kickoff_at = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        input_formats=['%Y-%m-%dT%H:%M'],
    )

    class Meta:
        model = Fixture
        fields = ['home_team', 'away_team', 'kickoff_at', 'stage', 'venue', 'is_knockout']
        widgets = {
            'home_team': forms.Select(attrs={'class': 'choices-select'}),
            'away_team': forms.Select(attrs={'class': 'choices-select'}),
            'stage': forms.TextInput(attrs={'placeholder': 'e.g. Group Stage, Round of 16, Final'}),
            'venue': forms.TextInput(attrs={'placeholder': 'e.g. Estadio Azteca, Mexico City'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        home_team = cleaned_data.get('home_team')
        away_team = cleaned_data.get('away_team')
        if home_team and away_team and home_team == away_team:
            raise forms.ValidationError('Home team and away team must be different.')
        return cleaned_data


class MatchResultForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['home_score', 'away_score']
        widgets = {
            'home_score': forms.NumberInput(attrs={'min': 0, 'class': 'form-control form-control-sm', 'style': 'width: 5rem'}),
            'away_score': forms.NumberInput(attrs={'min': 0, 'class': 'form-control form-control-sm', 'style': 'width: 5rem'}),
        }


class PenaltyResultForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['penalty_home_score', 'penalty_away_score']
        widgets = {
            'penalty_home_score': forms.NumberInput(attrs={'min': 0, 'class': 'form-control form-control-sm', 'style': 'width: 5rem', 'placeholder': '–'}),
            'penalty_away_score': forms.NumberInput(attrs={'min': 0, 'class': 'form-control form-control-sm', 'style': 'width: 5rem', 'placeholder': '–'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['penalty_home_score'].required = False
        self.fields['penalty_away_score'].required = False
