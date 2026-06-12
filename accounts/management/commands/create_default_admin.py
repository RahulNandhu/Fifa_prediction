from decouple import config
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Create (or update) the default admin superuser for this deployment.

    Run on every deploy so the hosted site always has a known admin login,
    without needing an interactive `createsuperuser`. Credentials are read
    from env vars with sensible defaults so they can be overridden per
    environment without code changes.
    """

    help = 'Create or update the default admin superuser.'

    def handle(self, *args, **options):
        User = get_user_model()

        username = config('DJANGO_ADMIN_USERNAME', default='Analystor')
        password = config('DJANGO_ADMIN_PASSWORD', default='Analystor@2026')
        email = config('DJANGO_ADMIN_EMAIL', default='')

        user, created = User.objects.get_or_create(username=username, defaults={'email': email})
        user.email = email or user.email
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        action = 'Created' if created else 'Updated'
        self.stdout.write(self.style.SUCCESS(f'{action} admin superuser "{username}".'))
