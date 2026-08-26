from django import forms
from django.contrib import admin,messages
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from datetime import timedelta
from django.utils import timezone
from .models import AuditLog, User, Organisation


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = ("code", "label", "description")
    search_fields = (
        "label__icontains",
        "description__icontains",
    )


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