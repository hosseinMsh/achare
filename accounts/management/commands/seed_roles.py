from django.core.management.base import BaseCommand

from accounts.models import Role


class Command(BaseCommand):
    help = 'Create default roles: customer, contractor, support, admin'

    def handle(self, *args, **options):
        for name in ['customer', 'contractor', 'support', 'admin']:
            Role.objects.get_or_create(name=name)
        self.stdout.write(self.style.SUCCESS('Default roles ensured.'))
