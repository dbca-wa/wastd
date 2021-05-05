# -*- coding: utf-8 -*-
"""User admin."""
from __future__ import absolute_import, unicode_literals
import logging

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.shortcuts import render

from .models import User

logger = logging.getLogger(__name__)

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
            {"fields": ("name", "nickname", "aliases", "role", "affiliation", "phone", "alive")}),
    ) + AuthUserAdmin.fieldsets
    list_filter = ("is_superuser", "is_staff", "is_active", "alive")
    list_display = (
        "username",
        "name",
        "nickname",
        "aliases",
        "role",
        "phone",
        "email",
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
