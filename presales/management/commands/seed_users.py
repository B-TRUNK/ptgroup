from django.core.management.base import BaseCommand
from django.db import transaction

from presales.models import Person


class Command(BaseCommand):

    help = "Create/update the default Protec users and permissions."

    PASSWORD = "CHANGE_THIS_PASSWORD"

    USERS = [
        {
            "email": "abanob.boschra@protec-gp.com",
            "first_name": "Abanob",
            "last_name": "Boschra",
            "role": Person.Role.DEVELOPER,
            "is_staff": True,
            "is_superuser": True,
        },
        {
            "email": "sherif.gad@protec-gp.com",
            "first_name": "Sherif",
            "last_name": "Gad",
            "role": Person.Role.ADMIN,
            "is_staff": True,
            "is_superuser": True,
        },
        {
            "email": "m.fawzy@protec-gp.com",
            "first_name": "M.",
            "last_name": "Fawzy",
            "role": Person.Role.VIEWER,
            "is_staff": True,
            "is_superuser": False,
        },
        {
            "email": "ahmed.fawzy@protec-gp.com",
            "first_name": "Ahmed",
            "last_name": "Fawzy",
            "role": Person.Role.VIEWER,
            "is_staff": True,
            "is_superuser": False,
        },
        {
            "email": "basma.nasser@protec-gp.com",
            "first_name": "Basma",
            "last_name": "Nasser",
            "role": Person.Role.MEMBER,
            "is_staff": True,
            "is_superuser": False,
        },
        {
            "email": "m.ramadan@protec-gp.com",
            "first_name": "M.",
            "last_name": "Ramadan",
            "role": Person.Role.MEMBER,
            "is_staff": True,
            "is_superuser": False,
        },
        {
            "email": "fatma.hussein@protec-gp.com",
            "first_name": "Fatma",
            "last_name": "Hussein",
            "role": Person.Role.MEMBER,
            "is_staff": True,
            "is_superuser": False,
        },
        {
            "email": "menna.abdelwahab@protec-gp.com",
            "first_name": "Menna",
            "last_name": "Abdelwahab",
            "role": Person.Role.MEMBER,
            "is_staff": True,
            "is_superuser": False,
        },
    ]

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "Seeding Protec users..."
            )
        )

        for data in self.USERS:

            email = data["email"]

            user, created = Person.objects.get_or_create(
                email=email
            )

            user.first_name = data["first_name"]
            user.last_name = data["last_name"]
            user.role = data["role"]

            user.is_active = True
            user.is_staff = data["is_staff"]
            user.is_superuser = data["is_superuser"]

            # Always set the deployment seed password.
            user.set_password(self.PASSWORD)

            user.save()

            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"CREATED: {email}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"UPDATED: {email}"
                    )
                )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "Protec users seeded successfully."
            )
        )