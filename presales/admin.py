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


# ============================================================
# FULL ADMIN
#
# Sherif + Abanob
#
# Also allows Django superusers.
# ============================================================

def is_full_admin(user):

    if not is_authenticated(user):
        return False

    if user.is_superuser:
        return True

    return user.email.lower() in (
        "sherif.gad@protec-gp.com",
        "abanob.boschra@protec-gp.com",
    )


# ============================================================
# MANAGEMENT
# ============================================================

def is_management(user):

    if not is_authenticated(user):
        return False

    return user.role == Person.Role.MANAGEMENT


# ============================================================
# DEVELOPER
# ============================================================

def is_developer(user):

    if not is_authenticated(user):
        return False

    return user.role == Person.Role.DEVELOPER


# ============================================================
# PRESALES ENGINEER
# ============================================================

def is_presales(user):

    if not is_authenticated(user):
        return False

    return user.role == Person.Role.PRESALES


# ============================================================
# CAN VIEW EVERYTHING
# ============================================================

def can_view_everything(user):

    return (
        is_full_admin(user)
        or is_management(user)
    )


# ============================================================
# CAN MANAGE PROJECT
#
# Full admins:
#     Any project
#
# Presales:
#     Only their own project
#
# Management:
#     View only
# ============================================================

def can_manage_project(user, project):

    if is_full_admin(user):
        return True

    if not is_presales(user):
        return False

    if project is None:
        return False

    return (
        project.presales_engineer_id
        == user.id
    )


# ============================================================
# CAN MANAGE VENDOR / DISTRIBUTOR CATALOG
#
# Presales + Developer + Full Admin
# ============================================================

def can_manage_vendor_catalog(user):

    return (
        is_full_admin(user)
        or is_presales(user)
        or is_developer(user)
    )


# ============================================================
# PERSON
# ============================================================

@admin.register(Person)
class PersonAdmin(UserAdmin):

    model = Person

    ordering = (
        "email",
    )

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
                "classes": (
                    "wide",
                ),
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

        return (
            is_full_admin(request.user)
            or is_management(request.user)
        )

    def has_view_permission(self, request, obj=None):

        return (
            is_full_admin(request.user)
            or is_management(request.user)
        )

    def has_add_permission(self, request):

        return (
            is_full_admin(request.user)
            or is_management(request.user)
        )

    def has_change_permission(self, request, obj=None):

        return is_full_admin(request.user)

    def has_delete_permission(self, request, obj=None):

        return is_full_admin(request.user)

    # ========================================================
    # AUTOCOMPLETE FILTER
    #
    # IMPORTANT:
    # Django autocomplete_fields does NOT use ProjectAdmin
    # get_form() to determine its result list.
    #
    # When Project.presales_engineer is being autocompleted,
    # only active PRESALES users are returned.
    #
    # Management / Developer users will NOT appear.
    # ========================================================

    def get_search_results(
        self,
        request,
        queryset,
        search_term
    ):

        queryset, use_distinct = super().get_search_results(
            request,
            queryset,
            search_term
        )

        # Detect Project -> presales_engineer autocomplete
        is_project_presales_autocomplete = (
            request.path.endswith(
                "/autocomplete/"
            )
            and request.GET.get(
                "field_name"
            ) == "presales_engineer"
        )

        if is_project_presales_autocomplete:

            queryset = queryset.filter(
                role=Person.Role.PRESALES,
                is_active=True
            )

        return queryset, use_distinct


# ============================================================
# LIGHT CURRENT SYSTEM
#
# Full Admin:
#     View / Add / Edit / Delete
#
# Management + Presales:
#     View only
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

        user = request.user

        return (
            is_full_admin(user)
            or is_management(user)
            or is_presales(user)
        )

    def has_view_permission(self, request, obj=None):

        user = request.user

        return (
            is_full_admin(user)
            or is_management(user)
            or is_presales(user)
        )

    def has_add_permission(self, request):

        return is_full_admin(request.user)

    def has_change_permission(self, request, obj=None):

        return is_full_admin(request.user)

    def has_delete_permission(self, request, obj=None):

        return is_full_admin(request.user)


# ============================================================
# DISTRIBUTOR INLINE
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

    def has_add_permission(self, request, obj=None):

        return can_manage_vendor_catalog(
            request.user
        )

    def has_change_permission(self, request, obj=None):

        return can_manage_vendor_catalog(
            request.user
        )

    def has_delete_permission(self, request, obj=None):

        return can_manage_vendor_catalog(
            request.user
        )


# ============================================================
# VENDOR
#
# Full Admin + Presales + Developer:
#     View / Add / Edit / Delete
#
# Management:
#     View only
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

        user = request.user

        return (
            is_full_admin(user)
            or is_management(user)
            or is_presales(user)
            or is_developer(user)
        )

    def has_view_permission(self, request, obj=None):

        user = request.user

        return (
            is_full_admin(user)
            or is_management(user)
            or is_presales(user)
            or is_developer(user)
        )

    def has_add_permission(self, request):

        return can_manage_vendor_catalog(
            request.user
        )

    def has_change_permission(self, request, obj=None):

        return can_manage_vendor_catalog(
            request.user
        )

    def has_delete_permission(self, request, obj=None):

        return can_manage_vendor_catalog(
            request.user
        )


# ============================================================
# DISTRIBUTOR
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

        user = request.user

        return (
            is_full_admin(user)
            or is_management(user)
            or is_presales(user)
            or is_developer(user)
        )

    def has_view_permission(self, request, obj=None):

        user = request.user

        return (
            is_full_admin(user)
            or is_management(user)
            or is_presales(user)
            or is_developer(user)
        )

    def has_add_permission(self, request):

        return can_manage_vendor_catalog(
            request.user
        )

    def has_change_permission(self, request, obj=None):

        return can_manage_vendor_catalog(
            request.user
        )

    def has_delete_permission(self, request, obj=None):

        return can_manage_vendor_catalog(
            request.user
        )


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
            obj.project_system.project
        )

    def has_delete_permission(self, request, obj=None):

        if obj is None:
            return False

        return can_manage_project(
            request.user,
            obj.project_system.project
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
            obj
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


# ============================================================
# PROJECT SYSTEM INLINE
#
# Shows:
#
# System
# Status
# Offer Amount
# Currency
# ============================================================

class ProjectSystemInline(admin.TabularInline):

    model = ProjectSystem

    extra = 1

    fields = (
        "system",
        "status",
        "offer_amount",
        "offer_currency",
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
        "phase",
        "status",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "phase",
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
                    "phase",
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

    # ========================================================
    # PRESALES ENGINEER DROPDOWN
    #
    # Only active PRESALES users appear.
    # ========================================================

    def get_form(self, request, obj=None, **kwargs):

        form = super().get_form(
            request,
            obj,
            **kwargs
        )

        if "presales_engineer" in form.base_fields:

            form.base_fields[
                "presales_engineer"
            ].queryset = Person.objects.filter(
                role=Person.Role.PRESALES,
                is_active=True
            ).order_by(
                "first_name",
                "last_name",
                "email"
            )

        return form

    # ========================================================
    # MODULE
    # ========================================================

    def has_module_permission(self, request):

        user = request.user

        return (
            is_full_admin(user)
            or is_management(user)
            or is_presales(user)
        )

    # ========================================================
    # QUERYSET
    # ========================================================

    def get_queryset(self, request):

        qs = super().get_queryset(request)

        user = request.user

        if is_full_admin(user):
            return qs

        if is_management(user):
            return qs

        if is_presales(user):
            return qs.filter(
                presales_engineer=user
            )

        return qs.none()

    # ========================================================
    # VIEW
    # ========================================================

    def has_view_permission(self, request, obj=None):

        user = request.user

        if is_full_admin(user):
            return True

        if is_management(user):
            return True

        if is_presales(user):

            if obj is None:
                return True

            return (
                obj.presales_engineer_id
                == user.id
            )

        return False

    # ========================================================
    # ADD
    #
    # Only Full Admin can create projects.
    # ========================================================

    def has_add_permission(self, request):

        return is_full_admin(
            request.user
        )

    # ========================================================
    # CHANGE
    # ========================================================

    def has_change_permission(self, request, obj=None):

        user = request.user

        if is_full_admin(user):
            return True

        if is_management(user):
            return False

        if is_presales(user):

            if obj is None:
                return False

            return (
                obj.presales_engineer_id
                == user.id
            )

        return False

    # ========================================================
    # DELETE
    # ========================================================

    def has_delete_permission(self, request, obj=None):

        return is_full_admin(
            request.user
        )


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

        return (
            is_full_admin(request.user)
            or is_management(request.user)
            or is_presales(request.user)
        )

    def get_queryset(self, request):

        qs = super().get_queryset(request)

        user = request.user

        if is_full_admin(user):
            return qs

        if is_management(user):
            return qs

        if is_presales(user):

            return qs.filter(
                project_system__project__presales_engineer=user
            )

        return qs.none()

    def has_view_permission(self, request, obj=None):

        user = request.user

        if is_full_admin(user):
            return True

        if is_management(user):
            return True

        if is_presales(user):

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
            or is_presales(request.user)
        )

    def has_change_permission(self, request, obj=None):

        user = request.user

        if is_full_admin(user):
            return True

        if not is_presales(user):
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

        if not is_presales(user):
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

        return (
            is_full_admin(request.user)
            or is_management(request.user)
            or is_presales(request.user)
        )

    def get_queryset(self, request):

        qs = super().get_queryset(request)

        user = request.user

        if is_full_admin(user):
            return qs

        if is_management(user):
            return qs

        if is_presales(user):

            return qs.filter(
                project_vendor__project_system__project__presales_engineer=user
            )

        return qs.none()

    def has_view_permission(self, request, obj=None):

        user = request.user

        if is_full_admin(user):
            return True

        if is_management(user):
            return True

        if is_presales(user):

            if obj is None:
                return True

            return (
                obj.project_vendor
                .project_system
                .project
                .presales_engineer_id
                == user.id
            )

        return False

    def has_add_permission(self, request):

        return (
            is_full_admin(request.user)
            or is_presales(request.user)
        )

    def has_change_permission(self, request, obj=None):

        user = request.user

        if is_full_admin(user):
            return True

        if not is_presales(user):
            return False

        if obj is None:
            return False

        return (
            obj.project_vendor
            .project_system
            .project
            .presales_engineer_id
            == user.id
        )

    def has_delete_permission(self, request, obj=None):

        user = request.user

        if is_full_admin(user):
            return True

        if not is_presales(user):
            return False

        if obj is None:
            return False

        return (
            obj.project_vendor
            .project_system
            .project
            .presales_engineer_id
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
        "status",
        "offer_amount",
        "offer_currency",
    )

    list_filter = (
        "status",
        "offer_currency",
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
    # QUERYSET
    # ========================================================

    def get_queryset(self, request):

        qs = super().get_queryset(request)

        user = request.user

        if is_full_admin(user):
            return qs

        if is_management(user):
            return qs

        if is_presales(user):

            return qs.filter(
                project__presales_engineer=user
            )

        return qs.none()

    # ========================================================
    # MODULE
    # ========================================================

    def has_module_permission(self, request):

        return (
            is_full_admin(request.user)
            or is_management(request.user)
            or is_presales(request.user)
        )

    # ========================================================
    # VIEW
    # ========================================================

    def has_view_permission(self, request, obj=None):

        user = request.user

        if is_full_admin(user):
            return True

        if is_management(user):
            return True

        if is_presales(user):

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

        return (
            is_full_admin(request.user)
            or is_presales(request.user)
        )

    # ========================================================
    # CHANGE
    # ========================================================

    def has_change_permission(self, request, obj=None):

        user = request.user

        if is_full_admin(user):
            return True

        if not is_presales(user):
            return False

        if obj is None:
            return False

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

        if not is_presales(user):
            return False

        if obj is None:
            return False

        return (
            obj.project.presales_engineer_id
            == user.id
        )