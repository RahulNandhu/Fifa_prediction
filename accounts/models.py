from django.conf import settings
from django.db import models


class KnockoutModalDismissal(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='knockout_modal_dismissal',
    )
    dismissed = models.BooleanField(default=False)
    admin_dismissed = models.BooleanField(default=False)
