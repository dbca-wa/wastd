from datetime import timedelta

from django import forms
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils import timezone

from .models import AuditLog, Organisation, OrganisationExportAssignment, User
from wamtram2.models import TrtLocations

@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = ("code", "label", "description")
    search_fields = (
        "label__icontains",
        "description__icontains",
    )

class OrganisationExportAssignmentForm(forms.ModelForm):
    location_code = forms.ChoiceField(label="Location")

    class Meta:
        model = OrganisationExportAssignment
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["location_code"].choices = [
            (location.location_code, location.location_name)
            for location in TrtLocations.get_ordered_locations()
        ]

        self.fields["valid_from"].required = False
        self.fields["valid_to"].required = False

        for field_name in ("data_from", "data_to", "valid_from", "valid_to"):
            self.fields[field_name].widget.attrs["placeholder"] = "DD/MM/YYYY"

    def clean(self):
        cleaned_data = super().clean()

        data_from = cleaned_data.get("data_from")
        data_to = cleaned_data.get("data_to")
        validity_type = cleaned_data.get("validity_type")
        valid_from = cleaned_data.get("valid_from")
        valid_to = cleaned_data.get("valid_to")

        if data_from and data_to and data_from > data_to:
            self.add_error("data_to", "Data to must be on or after Data from.")

        if validity_type == OrganisationExportAssignment.ValidityType.TIME_LIMITED:
            if not valid_from:
                self.add_error("valid_from", "Valid from is required for time-limited access.")

            if not valid_to:
                self.add_error("valid_to", "Valid to is required for time-limited access.")

            if valid_from and valid_to and valid_from > valid_to:
                self.add_error("valid_to", "Valid to must be on or after Valid from.")

        elif validity_type == OrganisationExportAssignment.ValidityType.PERMANENT:
            cleaned_data["valid_from"] = None
            cleaned_data["valid_to"] = None

        return cleaned_data

class LocationFilter(admin.SimpleListFilter):
    title = "Location"
    parameter_name = "location_code"

    def lookups(self, request, model_admin):
        return [
            (location.location_code, location.location_name)
            for location in TrtLocations.get_ordered_locations()
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(location_code=self.value())

        return queryset

@admin.register(OrganisationExportAssignment)
class OrganisationExportAssignmentAdmin(admin.ModelAdmin):
    form = OrganisationExportAssignmentForm

    list_display = (
        "organisation",
        "location",
        "data_from",
        "data_to",
        "validity_type",
        "valid_from",
        "valid_to",
        "current_status",
    )

    list_filter = (
        "organisation",
         LocationFilter,
        "validity_type",
    )

    search_fields = (
        "organisation__code",
        "organisation__label",
        "location_code",
    )

    @admin.display(description="Location")
    def location(self, obj):
        try:
            return TrtLocations.objects.get(
                location_code=obj.location_code
            ).location_name
        except TrtLocations.DoesNotExist:
            return obj.location_code
    @admin.display(description="Current status")
    def current_status(self, obj):
        return obj.current_status
    class Media:
        js = ("js/organisation_export_assignment.js",)
class UserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class UserCreationForm(UserCreationForm):
    error_message = UserCreationForm.error_messages.update({"duplicate_username": "This username has already been taken."})

    class Meta(UserCreationForm.Meta):
        model = User

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages["duplicate_username"])


@admin.register(User)
class UserAdmin(AuthUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    fieldsets = (
        (
            "User Profile",
            {
                "fields": (
                    "name",
                    "nickname",
                    "aliases",
                    "role",
                    "affiliation",
                    "organisations",
                    "phone",
                    "alive",
                    "can_access_tracks_nests",
                    "can_access_tagging",
                    "can_access_marine_wildlife",
                )
            },
        ),
    ) + AuthUserAdmin.fieldsets
    list_filter = (
        "is_superuser",
        "is_staff",
        "is_active",
        "alive",
    )
    list_display = (
        "username",
        "email",
        "name",
        "nickname",
        "aliases",
        "role",
        "phone",
        "is_superuser",
        "is_staff",
        "is_active",
        "alive",
        "can_access_tracks_nests",
        "can_access_tagging",
        "can_access_marine_wildlife",
    )
    search_fields = [
        "email",
        "username",
        "name",
        "nickname",
        "aliases",
        "role",
        "affiliation",
        "phone",
    ]
    readonly_fields = [
        "organisations",
        "is_superuser",
        "is_staff",
    ]

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)

        if request.user.is_superuser:
            return fieldsets

        return tuple(
            (
                name,
                {
                    **options,
                    "fields": tuple(
                        field
                        for field in options.get("fields", ())
                        if field != "password"
                    ),
                },
            )
            for name, options in fieldsets
        )

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_staff:
            if request.user.is_superuser:
                return []
            else:
                return [f.name for f in self.model._meta.fields]


@admin.action(
    description="Delete all audit logs older than 1 year",
    permissions=["delete"],
)

def delete_audit_logs_older_than_one_year(modeladmin, request, queryset):
    cutoff = timezone.now() - timedelta(days=365)
    deleted_count, _ = AuditLog.objects.filter(created_at__lt=cutoff).delete()
    modeladmin.message_user(
        request,
        f"Deleted {deleted_count} audit logs older than 1 year.",
        messages.SUCCESS,
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "action",
        "actor",
        "app_label",
        "model_name",
        "object_pk",
        "object_repr",
        "path",
    )
    list_filter = ("action", "app_label", "model_name", "created_at")
    search_fields = ("actor__username", "actor__email", "object_pk", "object_repr", "path")
    readonly_fields = (
        "created_at",
        "action",
        "app_label",
        "model_name",
        "object_pk",
        "object_repr",
        "actor",
        "path",
        "method",
        "remote_addr",
    )
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_per_page = 50
    actions = (delete_audit_logs_older_than_one_year,)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        if not request.user.is_superuser:
            return False

        # Changelist / custom action permission check
        if obj is None:
            return True

        cutoff = timezone.now() - timedelta(days=365)
        return obj.created_at < cutoff

    def get_actions(self, request):
        actions = super().get_actions(request)
        actions.pop("delete_selected", None)
        return actions
