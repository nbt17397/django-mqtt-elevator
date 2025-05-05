from django.core.management.base import BaseCommand
from django.utils import timezone
from elevator.models import BoardControlRequest

class Command(BaseCommand):
    help = 'Expire board control requests that are past their expiration time'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        expired = BoardControlRequest.objects.filter(is_active=True, expires_at__lte=now)
        count = expired.update(is_active=False)
        self.stdout.write(f'{count} expired control requests updated.')
