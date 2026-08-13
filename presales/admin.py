from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    Person,
    LightCurrentSystem,
    Vendor,
    Distributor,
    Project,
    ProjectSystem,
    ProjectVendor,
    ProjectDistributor,
)


# ============================================================
# PROTEC ADMIN BRANDING
# ============================================================

admin.site.site_header = "Protec Administration"
admin.site.site_title = "Protec Admin"
admin.site.index_title = "Protec Management"


# ============================================================
# PERMISSION HELPERS
# ============================================================

def is_authenticated(user):

    return (
        user is not None
        and user.is_authenticated
    )


def is_full_admin(user):

    if not is_authenticated(user):
        return False

    return user.is_superuser


def is_viewer(user):

    if not is_authenticated(user):
        return False

    return user.role == Person.Role.VIEWER


def is_menna(user):

    if not is_authenticated(user):
        return False

    return user.email.lower() == (
        "menna.abdelwahab@protec-gp.com"
    )


def is_member(user):

    if not is_authenticated(user):
        return False

    return user.role == Person.Role.MEMBER


def can_manage_project(user, project):

    if is_full_admin(user):
        return True

    if is_viewer(user):
        return False

    if project is None:
        return False

    return (
        project.presales_engineer_id
        == user.id
    )


# ============================================================
# PERSON
# ============================================================

@admin.register(Person)
class PersonAdmin(UserAdmin):

    model = Person

    ordering = ("email",)

    list_display = (
        "email",
        "first_name",
        "last_name",
        "role",
        "is_active",
        "is_staff",
        "is_superuser",
    )

    list_filter = (
        "role",
        "is_active",
        "is_staff",
        "is_superuser",
    )

    search_fields = (
        "email",
        "first_name",
        "last_name",
    )

    fieldsets = (
        (
            "Account",
            {
                "fields": (
                    "email",
                    "password",
                )
            },
        ),
        (
            "Personal Information",
            {
                "fields": (
                    "first_name",
                    "last_name",
                )
            },
        ),
        (
            "Protec Role",
            {
                "fields": (
                    "role",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Important Dates",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                    "role",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )

    def has_module_permission(self, request):
        return is_full_admin(request.user)

    def has_view_permission(self, request, obj=None):
        return is_full_admin(request.user)

    def has_add_permission(self, request):
        return is_full_admin(request.user)

    def has_change_permission(self, request, obj=None):
        return is_full_admin(request.user)

    def has_delete_permission(self, request, obj=None):
        return is_full_admin(request.user)


# ============================================================
# LIGHT CURRENT SYSTEM
#
# ONLY ADMIN / DEVELOPER
# ============================================================

@admin.register(LightCurrentSystem)
class LightCurrentSystemAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "description",
    )

    search_fields = (
        "name",
        "description",
    )

    ordering = (
        "name",
    )

    def has_module_permission(self, request):
        """
        Everyone who can access the admin dashboard
        can see the Light Current Systems section.
        """
        user = request.user

        return (
            is_full_admin(user)
            or is_viewer(user)
            or is_menna(user)
            or is_member(user)
        )

    def has_view_permission(self, request, obj=None):
        """
        Everyone can view Light Current Systems.
        """
        user = request.user

        return (
            is_full_admin(user)
            or is_viewer(user)
            or is_menna(user)
            or is_member(user)
        )

    def has_add_permission(self, request):
        """
        Only Abanob / Sherif can create systems.
        """
        return is_full_admin(request.user)

    def has_change_permission(self, request, obj=None):
        """
        Only Abanob / Sherif can modify systems.
        """
        return is_full_admin(request.user)

    def has_delete_permission(self, request, obj=None):
        """
        Only Abanob / Sherif can delete systems.
        """
        return is_full_admin(request.user)


# ============================================================
# DISTRIBUTOR INLINE
#
# Inside Vendor:
#
# Vendor
#   ├── Distributor 1
#   ├── Distributor 2
#   └── Distributor 3
# ============================================================

class DistributorInline(admin.TabularInline):

    model = Distributor

    extra = 1

    fields = (
        "name",
        "contact_1_name",
        "contact_1_mobile",
        "contact_1_email",
        "contact_2_name",
        "contact_2_mobile",
        "contact_2_email",
        "notes",
    )


# ============================================================
# VENDOR
#
# Anyone can view/add/change/delete.
#
# Vendor belongs to one Light Current System.
# ============================================================

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "system",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "system",
    )

    search_fields = (
        "name",
        "system__name",
    )

    autocomplete_fields = (
        "system",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    inlines = (
        DistributorInline,
    )

    ordering = (
        "system__name",
        "name",
    )

    def has_module_permission(self, request):

        return is_authenticated(request.user)

    def has_view_permission(self, request, obj=None):

        return is_authenticated(request.user)

    def has_add_permission(self, request):

        return is_authenticated(request.user)

    def has_change_permission(self, request, obj=None):

        return is_authenticated(request.user)

    def has_delete_permission(self, request, obj=None):

        return is_authenticated(request.user)


# ============================================================
# DISTRIBUTOR
#
# Anyone can view/add/change/delete.
# ============================================================

@admin.register(Distributor)
class DistributorAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "vendor",
        "contact_1_name",
        "contact_1_mobile",
        "contact_1_email",
        "contact_2_name",
        "contact_2_mobile",
        "contact_2_email",
    )

    list_filter = (
        "vendor__system",
        "vendor",
    )

    search_fields = (
        "name",
        "vendor__name",
        "vendor__system__name",
        "contact_1_name",
        "contact_1_email",
        "contact_2_name",
        "contact_2_email",
    )

    autocomplete_fields = (
        "vendor",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "vendor__system__name",
        "vendor__name",
        "name",
    )

    def has_module_permission(self, request):

        return is_authenticated(request.user)

    def has_view_permission(self, request, obj=None):

        return is_authenticated(request.user)

    def has_add_permission(self, request):

        return is_authenticated(request.user)

    def has_change_permission(self, request, obj=None):

        return is_authenticated(request.user)

    def has_delete_permission(self, request, obj=None):

        return is_authenticated(request.user)


# ============================================================
# PROJECT DISTRIBUTOR INLINE
# ============================================================

class ProjectDistributorInline(admin.TabularInline):

    model = ProjectDistributor

    extra = 1

    fields = (
        "distributor",
    )

    autocomplete_fields = (
        "distributor",
    )

    show_change_link = True

    def has_view_permission(self, request, obj=None):

        return is_authenticated(request.user)

    def has_add_permission(self, request, obj=None):

        if obj is None:
            return False

        return can_manage_project(
            request.user,
            obj.project_system.project
        )

    def has_change_permission(self, request, obj=None):

        if obj is None:
            return False

        return can_manage_project(
            request.user,
            obj.project_vendor.project_system.project
        )

    def has_delete_permission(self, request, obj=None):

        if obj is None:
            return False

        return can_manage_project(
            request.user,
            obj.project_vendor.project_system.project
        )


# ============================================================
# PROJECT VENDOR INLINE
# ============================================================

class ProjectVendorInline(admin.TabularInline):

    model = ProjectVendor

    extra = 1

    fields = (
        "vendor",
    )

    autocomplete_fields = (
        "vendor",
    )

    show_change_link = True

    def has_view_permission(self, request, obj=None):

        return is_authenticated(request.user)

    def has_add_permission(self, request, obj=None):

        if obj is None:
            return False

        return can_manage_project(
            request.user,
            obj.project
        )

    def has_change_permission(self, request, obj=None):

        if obj is None:
            return False

        return can_manage_project(
            request.user,
            obj.project_system.project
        )

    def has_delete_permission(self, request, obj=None):

        if obj is None:
            return False

        return can_manage_project(
            request.user,
            obj.project_system.project
        )

    inlines = (
        ProjectDistributorInline,
    )


# ============================================================
# PROJECT SYSTEM INLINE
# ============================================================

class ProjectSystemInline(admin.TabularInline):

    model = ProjectSystem

    extra = 1

    fields = (
        "system",
    )

    autocomplete_fields = (
        "system",
    )

    show_change_link = True

    def has_view_permission(self, request, obj=None):

        return is_authenticated(request.user)

    def has_add_permission(self, request, obj=None):

        if obj is None:
            return False

        return can_manage_project(
            request.user,
            obj
        )

    def has_change_permission(self, request, obj=None):

        if obj is None:
            return False

        return can_manage_project(
            request.user,
            obj
        )

    def has_delete_permission(self, request, obj=None):

        if obj is None:
            return False

        return can_manage_project(
            request.user,
            obj
        )


# ============================================================
# PROJECT
# ============================================================

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "presales_engineer",
        "status",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "status",
        "presales_engineer",
    )

    search_fields = (
        "name",
        "presales_engineer__email",
        "presales_engineer__first_name",
        "presales_engineer__last_name",
    )

    autocomplete_fields = (
        "presales_engineer",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Project Information",
            {
                "fields": (
                    "name",
                    "status",
                    "presales_engineer",
                )
            },
        ),
        (
            "Comments",
            {
                "fields": (
                    "comments",
                )
            },
        ),
        (
            "Dates",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    inlines = (
        ProjectSystemInline,
    )

    ordering = (
        "-updated_at",
    )

    # --------------------------------------------------------
    # MODULE
    # --------------------------------------------------------

    def has_module_permission(self, request):

        user = request.user

        return (
            is_full_admin(user)
            or is_viewer(user)
            or is_menna(user)
            or is_member(user)
        )

    # --------------------------------------------------------
    # QUERYSET
    # --------------------------------------------------------

    def get_queryset(self, request):

        qs = super().get_queryset(request)

        user = request.user

        if is_full_admin(user):
            return qs

        if is_viewer(user):
            return qs

        if is_menna(user):
            return qs

        if is_member(user):

            return qs.filter(
                presales_engineer=user
            )

        return qs.none()

    # --------------------------------------------------------
    # VIEW
    # --------------------------------------------------------

    def has_view_permission(self, request, obj=None):

        user = request.user

        if is_full_admin(user):
            return True

        if is_viewer(user):
            return True

        if is_menna(user):
            return True

        if is_member(user):

            if obj is None:
                return True

            return (
                obj.presales_engineer_id
                == user.id
            )

        return False

    # --------------------------------------------------------
    # ADD
    # --------------------------------------------------------

    def has_add_permission(self, request):

        return is_full_admin(request.user)

    # --------------------------------------------------------
    # CHANGE
    # --------------------------------------------------------

    def has_change_permission(self, request, obj=None):

        user = request.user

        if is_full_admin(user):
            return True

        if is_viewer(user):
            return False

        if obj is None:
            return False

        return (
            obj.presales_engineer_id
            == user.id
        )

    # --------------------------------------------------------
    # DELETE
    # --------------------------------------------------------

    def has_delete_permission(self, request, obj=None):

        return is_full_admin(request.user)


# ============================================================
# PROJECT VENDOR
# ============================================================

@admin.register(ProjectVendor)
class ProjectVendorAdmin(admin.ModelAdmin):

    list_display = (
        "project_system",
        "vendor",
    )

    list_filter = (
        "vendor__system",
        "vendor",
    )

    search_fields = (
        "project_system__project__name",
        "project_system__system__name",
        "vendor__name",
    )

    autocomplete_fields = (
        "project_system",
        "vendor",
    )

    def has_module_permission(self, request):

        return is_authenticated(request.user)

    def get_queryset(self, request):

        qs = super().get_queryset(request)

        user = request.user

        if is_full_admin(user):
            return qs

        if is_viewer(user):
            return qs

        if is_menna(user):
            return qs

        if is_member(user):

            return qs.filter(
                project_system__project__presales_engineer=user
            )

        return qs.none()

    def has_view_permission(self, request, obj=None):

        user = request.user

        if is_full_admin(user):
            return True

        if is_viewer(user):
            return True

        if is_menna(user):
            return True

        if is_member(user):

            if obj is None:
                return True

            return (
                obj.project_system.project.presales_engineer_id
                == user.id
            )

        return False

    def has_add_permission(self, request):

        return (
            is_full_admin(request.user)
            or is_menna(request.user)
            or is_member(request.user)
        )

    def has_change_permission(self, request, obj=None):

        user = request.user

        if is_full_admin(user):
            return True

        if is_viewer(user):
            return False

        if obj is None:
            return False

        return (
            obj.project_system.project.presales_engineer_id
            == user.id
        )

    def has_delete_permission(self, request, obj=None):

        user = request.user

        if is_full_admin(user):
            return True

        if is_viewer(user):
            return False

        if obj is None:
            return False

        return (
            obj.project_system.project.presales_engineer_id
            == user.id
        )


# ============================================================
# PROJECT DISTRIBUTOR
# ============================================================

@admin.register(ProjectDistributor)
class ProjectDistributorAdmin(admin.ModelAdmin):

    list_display = (
        "project_vendor",
        "distributor",
    )

    list_filter = (
        "distributor__vendor__system",
        "distributor__vendor",
    )

    search_fields = (
        "project_vendor__project_system__project__name",
        "project_vendor__vendor__name",
        "distributor__name",
    )

    autocomplete_fields = (
        "project_vendor",
        "distributor",
    )

    def has_module_permission(self, request):

        return is_authenticated(request.user)

    def get_queryset(self, request):

        qs = super().get_queryset(request)

        user = request.user

        if is_full_admin(user):
            return qs

        if is_viewer(user):
            return qs

        if is_menna(user):
            return qs

        if is_member(user):

            return qs.filter(
                project_vendor__project_system__project__presales_engineer=user
            )

        return qs.none()

    def has_view_permission(self, request, obj=None):

        user = request.user

        if is_full_admin(user):
            return True

        if is_viewer(user):
            return True

        if is_menna(user):
            return True

        if is_member(user):

            if obj is None:
                return True

            return (
                obj.project_vendor.project_system.project.presales_engineer_id
                == user.id
            )

        return False

    def has_add_permission(self, request):

        return (
            is_full_admin(request.user)
            or is_menna(request.user)
            or is_member(request.user)
        )

    def has_change_permission(self, request, obj=None):

        user = request.user

        if is_full_admin(user):
            return True

        if is_viewer(user):
            return False

        if obj is None:
            return False

        return (
            obj.project_vendor.project_system.project.presales_engineer_id
            == user.id
        )

    def has_delete_permission(self, request, obj=None):

        user = request.user

        if is_full_admin(user):
            return True

        if is_viewer(user):
            return False

        if obj is None:
            return False

        return (
            obj.project_vendor.project_system.project.presales_engineer_id
            == user.id
        )


# ============================================================
# PROJECT SYSTEM
#
# STANDALONE VIEW
# ============================================================

@admin.register(ProjectSystem)
class ProjectSystemAdmin(admin.ModelAdmin):

    list_display = (
        "project",
        "system",
    )

    list_filter = (
        "system",
    )

    search_fields = (
        "project__name",
        "system__name",
    )

    autocomplete_fields = (
        "project",
        "system",
    )

    def has_module_permission(self, request):

        user = request.user

        return (
            is_full_admin(user)
            or is_viewer(user)
            or is_menna(user)
            or is_member(user)
        )

    def get_queryset(self, request):

        qs = super().get_queryset(request)

        user = request.user

        if is_full_admin(user):
            return qs

        if is_viewer(user):
            return qs

        if is_menna(user):
            return qs

        if is_member(user):

            return qs.filter(
                project__presales_engineer=user
            )

        return qs.none()

    def has_view_permission(self, request, obj=None):

        user = request.user

        if is_full_admin(user):
            return True

        if is_viewer(user):
            return True

        if is_menna(user):
            return True

        if is_member(user):

            if obj is None:
                return True

            return (
                obj.project.presales_engineer_id
                == user.id
            )

        return False

    def has_add_permission(self, request):

        return (
            is_full_admin(request.user)
            or is_menna(request.user)
            or is_member(request.user)
        )

    def has_change_permission(self, request, obj=None):

        user = request.user

        if is_full_admin(user):
            return True

        if is_viewer(user):
            return False

        if obj is None:
            return False

        return (
            obj.project.presales_engineer_id
            == user.id
        )

    def has_delete_permission(self, request, obj=None):

        user = request.user

        if is_full_admin(user):
            return True

        if is_viewer(user):
            return False

        if obj is None:
            return False

        return (
            obj.project.presales_engineer_id
            == user.id
        )