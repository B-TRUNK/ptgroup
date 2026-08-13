from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.db import models


# ============================================================
# PERSON / USER
# ============================================================

class PersonManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):

        if not email:
            raise ValueError("Email address is required")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            **extra_fields
        )

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault(
            "role",
            Person.Role.DEVELOPER
        )

        if extra_fields.get("is_staff") is not True:
            raise ValueError(
                "Superuser must have is_staff=True."
            )

        if extra_fields.get("is_superuser") is not True:
            raise ValueError(
                "Superuser must have is_superuser=True."
            )

        return self.create_user(
            email=email,
            password=password,
            **extra_fields
        )


class Person(AbstractBaseUser, PermissionsMixin):

    class Role(models.TextChoices):

        ADMIN = "ADMIN", "Admin"

        MEMBER = "MEMBER", "Member"

        VIEWER = "VIEWER", "Viewer"

        DEVELOPER = "DEVELOPER", "Developer"

    email = models.EmailField(
        unique=True,
        max_length=254
    )

    first_name = models.CharField(
        max_length=100,
        blank=True
    )

    last_name = models.CharField(
        max_length=100,
        blank=True
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.MEMBER
    )

    is_active = models.BooleanField(
        default=True
    )

    is_staff = models.BooleanField(
        default=False
    )

    date_joined = models.DateTimeField(
        auto_now_add=True
    )

    objects = PersonManager()

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = []

    def __str__(self):

        full_name = (
            f"{self.first_name} "
            f"{self.last_name}"
        ).strip()

        return full_name if full_name else self.email


# ============================================================
# LIGHT CURRENT SYSTEM
# ============================================================

class LightCurrentSystem(models.Model):

    name = models.CharField(
        max_length=200,
        unique=True
    )

    description = models.TextField(
        blank=True
    )

    def __str__(self):
        return self.name


# ============================================================
# PROJECT
# ============================================================

class Project(models.Model):

    class Status(models.TextChoices):

        TO_BE_ASSIGNED = (
            "TO_BE_ASSIGNED",
            "To Be Assigned"
        )

        IN_PROGRESS = (
            "IN_PROGRESS",
            "In Progress"
        )

    name = models.CharField(
        max_length=255
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.TO_BE_ASSIGNED
    )

    presales_engineer = models.ForeignKey(
        Person,
        on_delete=models.PROTECT,
        related_name="assigned_projects",
        null=True,
        blank=True
    )

    # ========================================================
    # COMMENTS
    #
    # Comments are now a simple field INSIDE the project.
    # ========================================================

    comments = models.TextField(
        blank=True,
        default=""
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name

    @property
    def is_assigned(self):
        return self.presales_engineer is not None


# ============================================================
# PROJECT SYSTEM
# ============================================================
#
# Relationship:
#
# Project
#    |
#    +---- ProjectSystem ---- LightCurrentSystem
#
# A project can have unlimited systems.
#
# Example:
#
# Hospital XYZ
#    CCTV
#    Access Control
#    Fire Alarm
#    Structured Cabling
#
# Same system cannot be added twice to the same project.
#
# ============================================================

class ProjectSystem(models.Model):

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="project_systems"
    )

    system = models.ForeignKey(
        LightCurrentSystem,
        on_delete=models.PROTECT,
        related_name="project_systems"
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "project",
                    "system",
                ],
                name="unique_project_system"
            )
        ]

        ordering = [
            "system__name"
        ]

    def __str__(self):

        return (
            f"{self.project.name} - "
            f"{self.system.name}"
        )