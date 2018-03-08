# -*- coding: utf-8 -*-
"""Taxonomy views."""
from __future__ import unicode_literals

# from django.shortcuts import render
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
# from django.views.generic import ListView, TemplateView
from django.http import HttpResponseRedirect
from taxonomy.utils import update_taxon as update_taxon_util

# Utilities ------------------------------------------------------------------#


@csrf_exempt
def update_taxon(request):
    """Update Taxon."""
    msg = update_taxon_util()
    messages.success(request, msg)
    return HttpResponseRedirect("/")
