import getpass

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.accounts.models import Role, User


class Command(BaseCommand):
    help = "Create the initial application ADMIN account."

    def handle(self, *args, **options):
        email = input("Email: ").strip()
        first_name = input("First name: ").strip()
        last_name = input("Last name: ").strip()
        password = getpass.getpass("Password: ")
        confirmation = getpass.getpass("Password confirmation: ")

        if not email:
            raise CommandError("Email is required.")
        if not first_name:
            raise CommandError("First name is required.")
        if not last_name:
            raise CommandError("Last name is required.")
        if password != confirmation:
            raise CommandError("Passwords do not match.")

        email = User.objects.normalize_email(email)
        if User.objects.filter(email__iexact=email).exists():
            raise CommandError("A user with this email already exists.")

        candidate = User(email=email, first_name=first_name, last_name=last_name)
        try:
            validate_password(password, user=candidate)
        except ValidationError as error:
            raise CommandError(" ".join(error.messages)) from error

        with transaction.atomic():
            role, _ = Role.objects.get_or_create(name=Role.ADMIN)
            User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role,
                is_active=True,
                is_staff=False,
                is_superuser=False,
            )

        self.stdout.write(self.style.SUCCESS("ADMIN account created successfully."))
