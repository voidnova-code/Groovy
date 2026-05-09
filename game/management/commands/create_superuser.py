from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Creates a superuser if none exists'

    def add_arguments(self, parser):
        parser.add_argument('--username', default='admin', help='Superuser username')
        parser.add_argument('--password', default='admin123', help='Superuser password')
        parser.add_argument('--email', default='', help='Superuser email')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = options['email'] or f'{username}@example.com'

        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(self.style.WARNING('Superuser already exists, skipping...'))
        else:
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" created!'))