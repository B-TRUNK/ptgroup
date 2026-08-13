from django.core.management.base import BaseCommand
from presales.models import Person


class Command(BaseCommand):

    help = "Seed Protec users"

    def handle(self, *args, **options):

        PASSWORD = "CHANGE_THIS_PASSWORD"

        users = [

            # ==================================================
            # FULL ADMIN / DEVELOPER
            # ==================================================

            {
                "email": "abanob.boschra@protec-gp.com",
                "first_name": "Abanob",
                "last_name": "Boschra",
                "role": Person.Role.DEVELOPER,
                "is_active": True,
                "is_staff": True,
                "is_superuser": True,
            },

            {
                "email": "sherif.gad@protec-gp.com",
                "first_name": "Sherif",
                "last_name": "Gad",
                "role": Person.Role.ADMIN,
                "is_active": True,
                "is_staff": True,
                "is_superuser": True,
            },

            # ==================================================
            # VIEWERS
            #
            # Can view everything.
            # Cannot modify projects.
            # ==================================================

            {
                "email": "m.fawzy@protec-gp.com",
                "first_name": "M.",
                "last_name": "Fawzy",
                "role": Person.Role.VIEWER,
                "is_active": True,
                "is_staff": True,
                "is_superuser": False,
            },

            {
                "email": "ahmed.fawzy@protec-gp.com",
                "first_name": "Ahmed",
                "last_name": "Fawzy",
                "role": Person.Role.VIEWER,
                "is_active": True,
                "is_staff": True,
                "is_superuser": False,
            },

            {
                "email": "hany.kamel@protec-gp.com",
                "first_name": "Hany",
                "last_name": "Kamel",
                "role": Person.Role.VIEWER,
                "is_active": True,
                "is_staff": True,
                "is_superuser": False,
            },

            # ==================================================
            # MEMBERS
            #
            # Can view and modify their assigned projects.
            # ==================================================

            {
                "email": "fatma.hussein@protec-gp.com",
                "first_name": "Fatma",
                "last_name": "Hussein",
                "role": Person.Role.MEMBER,
                "is_active": True,
                "is_staff": True,
                "is_superuser": False,
            },

            {
                "email": "basma.nasser@protec-gp.com",
                "first_name": "Basma",
                "last_name": "Nasser",
                "role": Person.Role.MEMBER,
                "is_active": True,
                "is_staff": True,
                "is_superuser": False,
            },

            {
                "email": "m.ramadan@protec-gp.com",
                "first_name": "M.",
                "last_name": "Ramadan",
                "role": Person.Role.MEMBER,
                "is_active": True,
                "is_staff": True,
                "is_superuser": False,
            },

            # ==================================================
            # MENNA
            #
            # Member role.
            # Special permissions are handled by admin.py
            # using her email.
            #
            # She can view everything and modify her
            # assigned projects.
            # ==================================================

            {
                "email": "menna.abdelwahab@protec-gp.com",
                "first_name": "Menna",
                "last_name": "Abdelwahab",
                "role": Person.Role.MEMBER,
                "is_active": True,
                "is_staff": True,
                "is_superuser": False,
            },
        ]

        # ======================================================
        # CREATE / UPDATE USERS
        # ======================================================

        for data in users:

            email = data["email"]

            user, created = Person.objects.get_or_create(
                email=email
            )

            # --------------------------------------------------
            # Update account information
            # --------------------------------------------------

            user.first_name = data["first_name"]
            user.last_name = data["last_name"]
            user.role = data["role"]
            user.is_active = data["is_active"]
            user.is_staff = data["is_staff"]
            user.is_superuser = data["is_superuser"]

            # --------------------------------------------------
            # Set password
            #
            # set_password() hashes the password correctly.
            # NEVER put the plain password directly into
            # user.password.
            # --------------------------------------------------

            user.set_password(PASSWORD)

            user.save()

            if created:

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created user: {email}"
                    )
                )

            else:

                self.stdout.write(
                    self.style.WARNING(
                        f"Updated user: {email}"
                    )
                )

        # ======================================================
        # FINISHED
        # ======================================================

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "=========================================="
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Protec user seeding completed successfully."
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "All seeded users use the default password:"
            )
        )

        self.stdout.write(
            self.style.WARNING(
                "CHANGE_THIS_PASSWORD"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "=========================================="
            )
        )