from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    Person,
    LightCurrentSystem,
    Project,
    ProjectSystem,
    ProjectComment,
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
    """
    Abanob + Sherif

    Full access to everything.
    """

    if not is_authenticated(user):
        return False

    return user.is_superuser


def is_viewer(user):
    """
    M. Fawzy + Ahmed Fawzy

    Can view everything.
    Cannot modify anything.
    """

    if not is_authenticated(user):
        return False

    return user.role == Person.Role.VIEWER


def is_menna(user):
    """
    Menna

    Can view everything.
    Can modify only projects assigned to her.
    """

    if not is_authenticated(user):
        return False

    return user.email.lower() == (
        "menna.abdelwahab@protec-gp.com"
    )


def is_member(user):
    """
    Fatma + Basma + M. Ramadan

    Can view and modify only their own projects.
    """

    if not is_authenticated(user):
        return False

    return user.role == Person.Role.MEMBER


# ============================================================
# PERSON / USERS
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
# MASTER SYSTEM CATALOG
#
# Only Abanob / Sherif can create/edit/delete systems.
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
# PROJECT SYSTEM INLINE
#
# Used inside Project.
#
# Example:
#
# Project
#   ├── CCTV
#   ├── Access Control
#   ├── Fire Alarm
#   └── Structured Cabling
#
# No duplicate systems are possible because the model
# has a unique constraint on:
#
# project + system
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
            return True

        return False

    # --------------------------------------------------------
    # ADD
    # --------------------------------------------------------

    def has_add_permission(self, request, obj=None):

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

    inlines = (
        ProjectSystemInline,
    )

    ordering = (
        "-updated_at",
    )

    # ========================================================
    # MODULE VISIBILITY
    # ========================================================

    def has_module_permission(self, request):

        user = request.user

        return (
            is_full_admin(user)
            or is_viewer(user)
            or is_menna(user)
            or is_member(user)
        )

    # ========================================================
    # QUERYSET
    # ========================================================

    def get_queryset(self, request):

        qs = super().get_queryset(request)

        user = request.user

        # Abanob / Sherif
        if is_full_admin(user):
            return qs

        # M. Fawzy / Ahmed
        if is_viewer(user):
            return qs

        # Menna
        # Can see ALL projects.
        if is_menna(user):
            return qs

        # Fatma / Basma / Ramadan
        # Can see ONLY their own projects.
        if is_member(user):
            return qs.filter(
                presales_engineer=user
            )

        return qs.none()

    # ========================================================
    # VIEW
    # ========================================================

    def has_view_permission(self, request, obj=None):

        user = request.user

        # Abanob / Sherif
        if is_full_admin(user):
            return True

        # M. Fawzy / Ahmed
        if is_viewer(user):
            return True

        # Menna
        if is_menna(user):
            return True

        # Members
        if is_member(user):

            if obj is None:
                return True

            return (
                obj.presales_engineer_id
                == user.id
            )

        return False

    # ========================================================
    # ADD
    # ========================================================
    #
    # Only Abanob / Sherif create projects.
    #
    # ========================================================

    def has_add_permission(self, request):

        return is_full_admin(request.user)

    # ========================================================
    # CHANGE
    # ========================================================
    #
    # IMPORTANT:
    #
    # obj is a PROJECT.
    #
    # Therefore we use:
    #
    # obj.presales_engineer_id
    #
    # NOT:
    #
    # obj.project
    #
    # ========================================================

    def has_change_permission(self, request, obj=None):

        user = request.user

        # Abanob / Sherif
        if is_full_admin(user):
            return True

        # M. Fawzy / Ahmed
        if is_viewer(user):
            return False

        # No object
        if obj is None:
            return False

        # Menna / Fatma / Basma / Ramadan
        #
        # Can modify ONLY their assigned projects.
        return (
            obj.presales_engineer_id
            == user.id
        )

    # ========================================================
    # DELETE
    # ========================================================
    #
    # Only Abanob / Sherif.
    #
    # ========================================================

    def has_delete_permission(self, request, obj=None):

        return is_full_admin(request.user)


# ============================================================
# PROJECT SYSTEM
#
# This is the standalone admin view of the relationship:
#
# Project <-> LightCurrentSystem
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

    # ========================================================
    # MODULE VISIBILITY
    # ========================================================

    def has_module_permission(self, request):

        user = request.user

        return (
            is_full_admin(user)
            or is_viewer(user)
            or is_menna(user)
            or is_member(user)
        )

    # ========================================================
    # QUERYSET
    # ========================================================

    def get_queryset(self, request):

        qs = super().get_queryset(request)

        user = request.user

        # Abanob / Sherif
        if is_full_admin(user):
            return qs

        # M. Fawzy / Ahmed
        if is_viewer(user):
            return qs

        # Menna
        if is_menna(user):
            return qs

        # Members
        if is_member(user):
            return qs.filter(
                project__presales_engineer=user
            )

        return qs.none()

    # ========================================================
    # VIEW
    # ========================================================

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

    # ========================================================
    # ADD
    # ========================================================

    def has_add_permission(self, request):

        user = request.user

        if is_full_admin(user):
            return True

        if is_viewer(user):
            return False

        if is_menna(user):
            return True

        if is_member(user):
            return True

        return False

    # ========================================================
    # CHANGE
    # ========================================================

    def has_change_permission(self, request, obj=None):

        user = request.user

        if is_full_admin(user):
            return True

        if is_viewer(user):
            return False

        if obj is None:
            return False

        # IMPORTANT:
        #
        # obj here IS ProjectSystem.
        #
        # Therefore obj.project is correct.
        #
        return (
            obj.project.presales_engineer_id
            == user.id
        )

    # ========================================================
    # DELETE
    # ========================================================

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


# ============================================================
# PROJECT COMMENT
# ============================================================

@admin.register(ProjectComment)
class ProjectCommentAdmin(admin.ModelAdmin):

    list_display = (
        "project",
        "author",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "author",
        "created_at",
    )

    search_fields = (
        "project__name",
        "author__email",
        "comment",
    )

    autocomplete_fields = (
        "project",
        "author",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    # ========================================================
    # MODULE VISIBILITY
    # ========================================================

    def has_module_permission(self, request):

        user = request.user

        return (
            is_full_admin(user)
            or is_viewer(user)
            or is_menna(user)
            or is_member(user)
        )

    # ========================================================
    # QUERYSET
    # ========================================================

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

    # ========================================================
    # VIEW
    # ========================================================

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

    # ========================================================
    # ADD
    # ========================================================

    def has_add_permission(self, request):

        user = request.user

        if is_full_admin(user):
            return True

        if is_viewer(user):
            return False

        if is_menna(user):
            return True

        if is_member(user):
            return True

        return False

    # ========================================================
    # CHANGE
    # ========================================================

    def has_change_permission(self, request, obj=None):

        user = request.user

        if is_full_admin(user):
            return True

        if is_viewer(user):
            return False

        if obj is None:
            return False

        # Users can edit ONLY their own comments.
        return (
            obj.author_id
            == user.id
        )

    # ========================================================
    # DELETE
    # ========================================================

    def has_delete_permission(self, request, obj=None):

        user = request.user

        if is_full_admin(user):
            return True

        if is_viewer(user):
            return False

        if obj is None:
            return False

        # Users can delete ONLY their own comments.
        return (
            obj.author_id
            == user.id
        )