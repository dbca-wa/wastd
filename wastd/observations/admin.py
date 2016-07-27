# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# from django import forms
from django.contrib import admin
from .models import Observation, MediaAttachment


# class MyUserChangeForm(UserChangeForm):
#     class Meta(UserChangeForm.Meta):
#         model = User
#
#
# class MyUserCreationForm(UserCreationForm):
#
#     error_message = UserCreationForm.error_messages.update({
#         'duplicate_username': 'This username has already been taken.'
#     })
#
#     class Meta(UserCreationForm.Meta):
#         model = User
#
#     def clean_username(self):
#         username = self.cleaned_data["username"]
#         try:
#             User.objects.get(username=username)
#         except User.DoesNotExist:
#             return username
#         raise forms.ValidationError(self.error_messages['duplicate_username'])

class MediaAttachmentInline(admin.TabularInline):
    model = MediaAttachment

@admin.register(Observation)
class ObservationAdmin(admin.ModelAdmin):
    # form = MyUserChangeForm
    # add_form = MyUserCreationForm
    # fieldsets = (
            # ('User Profile', {'fields': ('name',)}),
    # ) + AuthUserAdmin.fieldsets
    # list_display = ('username', 'name', 'is_superuser')
    # search_fields = ['name']
    inlines = [MediaAttachmentInline, ]
