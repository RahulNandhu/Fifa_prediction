from django.conf import settings
from django.db import models

from matches.models import Match, Outcome


class Prediction(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='predictions',
    )
    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name='predictions',
    )
    predicted_winner = models.CharField(max_length=4, choices=Outcome.choices)
    predicted_home_score = models.PositiveIntegerField()
    predicted_away_score = models.PositiveIntegerField()
    predicted_penalty_home_score = models.PositiveIntegerField(null=True, blank=True)
    predicted_penalty_away_score = models.PositiveIntegerField(null=True, blank=True)
    points_awarded = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'match')
        ordering = ['-match__fixture__kickoff_at']

    def __str__(self):
        return (
            f'{self.user} -> {self.match}: '
            f'{self.get_predicted_winner_display()}, '
            f'{self.predicted_home_score}-{self.predicted_away_score}'
        )


class PointTransaction(models.Model):
    class TransactionType(models.TextChoices):
        PREDICTION = 'PREDICTION', 'Prediction Score'
        ADJUSTMENT = 'ADJUSTMENT', 'Manual Adjustment'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='point_transactions',
    )
    points = models.IntegerField()
    transaction_type = models.CharField(
        max_length=12,
        choices=TransactionType.choices,
    )
    reason = models.CharField(max_length=255)
    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name='point_transactions',
        null=True,
        blank=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='point_adjustments_made',
        null=True,
        blank=True,
        help_text='Admin who made a manual adjustment.',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        sign = '+' if self.points >= 0 else ''
        return f'{self.user}: {sign}{self.points} ({self.get_transaction_type_display()})'

    @property
    def week_date(self):
        """Date used to bucket this transaction into a week for the weekly leaderboard."""
        if self.match_id:
            return self.match.fixture.kickoff_at.date()
        return self.created_at.date()
