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
#
# MASTER CATALOG
#
# Only ADMIN / DEVELOPER can create or modify systems.
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
# VENDOR
#
# A vendor belongs to ONE Light Current System.
#
# Example:
#
# FAS
#   ├── Simplex
#   ├── Honeywell
#   └── Eaton
# ============================================================

class Vendor(models.Model):

    system = models.ForeignKey(
        LightCurrentSystem,
        on_delete=models.PROTECT,
        related_name="vendors"
    )

    name = models.CharField(
        max_length=200
    )

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = [
            "system__name",
            "name",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "system",
                    "name",
                ],
                name="unique_vendor_per_system"
            )
        ]

    def __str__(self):

        return (
            f"{self.system.name} - "
            f"{self.name}"
        )


# ============================================================
# DISTRIBUTOR
#
# A distributor belongs to ONE vendor.
#
# Example:
#
# FAS
#   └── Simplex
#        ├── Distributor A
#        └── Distributor B
# ============================================================

class Distributor(models.Model):

    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name="distributors"
    )

    name = models.CharField(
        max_length=200
    )

    # --------------------------------------------------------
    # CONTACT 1
    # --------------------------------------------------------

    contact_1_name = models.CharField(
        max_length=200,
        blank=True
    )

    contact_1_mobile = models.CharField(
        max_length=100,
        blank=True
    )

    contact_1_email = models.EmailField(
        blank=True
    )

    # --------------------------------------------------------
    # CONTACT 2
    # --------------------------------------------------------

    contact_2_name = models.CharField(
        max_length=200,
        blank=True
    )

    contact_2_mobile = models.CharField(
        max_length=100,
        blank=True
    )

    contact_2_email = models.EmailField(
        blank=True
    )

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = [
            "vendor__system__name",
            "vendor__name",
            "name",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "vendor",
                    "name",
                ],
                name="unique_distributor_per_vendor"
            )
        ]

    def __str__(self):

        return (
            f"{self.vendor.name} - "
            f"{self.name}"
        )


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

    # --------------------------------------------------------
    # PROJECT COMMENTS
    # --------------------------------------------------------

    comments = models.TextField(
        blank=True
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
#
# Connects:
#
# Project <-> LightCurrentSystem
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


# ============================================================
# PROJECT VENDOR
#
# This represents a vendor actually selected for a system
# inside a specific project.
#
# Example:
#
# Project: Hospital XYZ
#
# FAS
#   ├── Simplex
#   └── Honeywell
#
# These vendors come from the global Vendor catalog.
# ============================================================

class ProjectVendor(models.Model):

    project_system = models.ForeignKey(
        ProjectSystem,
        on_delete=models.CASCADE,
        related_name="project_vendors"
    )

    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.PROTECT,
        related_name="project_vendor_selections"
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "project_system",
                    "vendor",
                ],
                name="unique_vendor_per_project_system"
            )
        ]

        ordering = [
            "vendor__name"
        ]

    def __str__(self):

        return (
            f"{self.project_system.project.name} - "
            f"{self.vendor.name}"
        )


# ============================================================
# PROJECT DISTRIBUTOR
#
# Represents a distributor selected for a vendor in a project.
#
# Example:
#
# Project
#   FAS
#     Simplex
#       Distributor A
#       Distributor B
# ============================================================

class ProjectDistributor(models.Model):

    project_vendor = models.ForeignKey(
        ProjectVendor,
        on_delete=models.CASCADE,
        related_name="project_distributors"
    )

    distributor = models.ForeignKey(
        Distributor,
        on_delete=models.PROTECT,
        related_name="project_distributor_selections"
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "project_vendor",
                    "distributor",
                ],
                name="unique_distributor_per_project_vendor"
            )
        ]

        ordering = [
            "distributor__name"
        ]

    def __str__(self):

        return (
            f"{self.project_vendor.project_system.project.name} - "
            f"{self.distributor.name}"
        )