from django import forms

from matches.models import Outcome

from .models import PointTransaction, Prediction


class PredictionForm(forms.ModelForm):
    class Meta:
        model = Prediction
        fields = ('predicted_winner', 'predicted_home_score', 'predicted_away_score')
        widgets = {
            'predicted_winner': forms.RadioSelect,
            'predicted_home_score': forms.NumberInput(attrs={'min': 0, 'class': 'form-control score-input', 'placeholder': '0'}),
            'predicted_away_score': forms.NumberInput(attrs={'min': 0, 'class': 'form-control score-input', 'placeholder': '0'}),
        }

    def __init__(self, *args, match=None, **kwargs):
        super().__init__(*args, **kwargs)
        if match is not None:
            self.fields['predicted_winner'].choices = [
                (Outcome.HOME, f'{match.home_team} to win'),
                (Outcome.DRAW, 'Draw'),
                (Outcome.AWAY, f'{match.away_team} to win'),
            ]


class PointAdjustmentForm(forms.ModelForm):
    class Meta:
        model = PointTransaction
        fields = ('points', 'reason')
        widgets = {
            'points': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm', 'style': 'width: 5.5rem;', 'placeholder': '+/- pts',
            }),
            'reason': forms.TextInput(attrs={
                'class': 'form-control form-control-sm', 'placeholder': 'Reason for adjustment',
            }),
        }

    def clean_points(self):
        points = self.cleaned_data['points']
        if points == 0:
            raise forms.ValidationError('Enter a non-zero point value.')
        return points
