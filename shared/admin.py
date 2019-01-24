# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# from django.contrib import admin
from django_fsm_log.admin import StateLogInline

# Register your models here.


class CustomStateLogInline(StateLogInline):
    """Custom StateLogInline."""

    classes = ('grp-collapse', 'grp-closed', 'wide', 'extrapretty', )
