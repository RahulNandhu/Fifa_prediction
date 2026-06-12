from datetime import timedelta

from django.conf import settings
from django.db import models


class Outcome(models.TextChoices):
    HOME = 'HOME', 'Home Win'
    AWAY = 'AWAY', 'Away Win'
    DRAW = 'DRAW', 'Draw'


# England and Scotland have no ISO 3166-1 country code of their own (they fall
# under GB), so their flags can't be derived from a 2-letter code via the regional
# indicator formula below. These are the Unicode tag-sequence flags for each.
_FLAG_OVERRIDES = {
    'EN': '\U0001F3F4\U000E0067\U000E0062\U000E0065\U000E006E\U000E0067\U000E007F',  # England
    'SC': '\U0001F3F4\U000E0067\U000E0062\U000E0073\U000E0063\U000E0074\U000E007F',  # Scotland
}


class Team(models.Model):
    """A national team, identified by its ISO 3166-1 alpha-2 country code."""

    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=2, unique=True, help_text='ISO 3166-1 alpha-2 country code, e.g. BR, DE.')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.flag} {self.name}'

    @property
    def flag(self):
        code = self.code.upper()
        if code in _FLAG_OVERRIDES:
            return _FLAG_OVERRIDES[code]
        return ''.join(chr(0x1F1E6 + ord(c) - ord('A')) for c in code)


class Fixture(models.Model):
    """A World Cup fixture, created by an admin via the Fixtures admin page."""

    home_team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name='home_fixtures')
    away_team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name='away_fixtures')
    kickoff_at = models.DateTimeField()
    stage = models.CharField(max_length=100, blank=True)
    venue = models.CharField(max_length=150, blank=True)

    class Meta:
        ordering = ['kickoff_at']

    def __str__(self):
        return f'{self.home_team} vs {self.away_team}'


class Match(models.Model):
    """A fixture that admins have published for prediction."""

    fixture = models.OneToOneField(
        Fixture,
        on_delete=models.CASCADE,
        related_name='match',
    )
    published = models.BooleanField(default=False)
    home_score = models.PositiveIntegerField(null=True, blank=True)
    away_score = models.PositiveIntegerField(null=True, blank=True)
    result_processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['fixture__kickoff_at']

    def __str__(self):
        return str(self.fixture)

    @property
    def kickoff_at(self):
        return self.fixture.kickoff_at

    @property
    def home_team(self):
        return self.fixture.home_team

    @property
    def away_team(self):
        return self.fixture.away_team

    @property
    def prediction_deadline(self):
        return self.fixture.kickoff_at - timedelta(
            minutes=settings.PREDICTION_DEADLINE_MINUTES_BEFORE_KICKOFF
        )

    @property
    def has_result(self):
        return self.home_score is not None and self.away_score is not None

    @property
    def actual_winner(self):
        if not self.has_result:
            return None
        if self.home_score > self.away_score:
            return Outcome.HOME
        if self.home_score < self.away_score:
            return Outcome.AWAY
        return Outcome.DRAW
