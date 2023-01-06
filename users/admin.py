"""User admin."""
import logging

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import User, Organisation

logger = logging.getLogger(__name__)


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    """Organisation admin."""

    list_display = ("code", "label", "description" )
    # list_filter = ("owner", "viewers")
    search_fields = ("label__icontains", "description__icontains", )
    # form = s2form(Organisation, attrs=S2ATTRS)
    # formfield_overrides = FORMFIELD_OVERRIDES


class MyUserChangeForm(UserChangeForm):

    class Meta(UserChangeForm.Meta):
        model = User


class MyUserCreationForm(UserCreationForm):

    error_message = UserCreationForm.error_messages.update({
        "duplicate_username": "This username has already been taken."
    })

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
class MyUserAdmin(AuthUserAdmin):
    form = MyUserChangeForm
    add_form = MyUserCreationForm
    fieldsets = (
        ("User Profile",
            {"fields": (
                "name",
                "nickname",
                "aliases",
                "role",
                "affiliation",
                "organisations",
                "phone",
                "alive")}),
    ) + AuthUserAdmin.fieldsets
    list_filter = ("is_superuser", "is_staff", "is_active", "alive",)
    list_display = (
        "username",
        "email",
        "name",
        "nickname",
        "aliases",
        # "organisations",
        "role",
        "phone",
        "is_superuser",
        "is_staff",
        "is_active",
        "alive"
    )
    search_fields = [
        "username__icontains",
        "name__icontains",
        "nickname__icontains",
        "aliases__icontains",
        "role__icontains",
        "affiliation__icontains",
        "email__icontains",
        "phone__icontains"
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
