# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
# from django.views.generic import ListView, TemplateView
from django.http import HttpResponseRedirect


# Utilities ------------------------------------------------------------------#
@csrf_exempt
def update_taxon(request):
    """Update Taxon."""
    from taxonomy.utils import update_taxon
    update_taxon()
    msg = "Taxon names updated."
    messages.success(request, msg)
    return HttpResponseRedirect("/")
