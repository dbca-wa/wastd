# -*- coding: utf-8 -*-
"""Occurrence views."""
from __future__ import unicode_literals

# from django.shortcuts import render
from django.views.generic.edit import (
    # FormView,
    CreateView
    # DeleteView,
    # UpdateView
)

# ModelForms
from .forms import (AreaEncounterForm, TaxonAreaEncounterForm, CommunityAreaEncounterForm)

# select2 forms
# from .admin import (AreaForm, TaxonAreaForm, CommunityAreaForm)


class AreaEncounterCreateView(CreateView):
    """Create view for AreaEncounter."""

    template_name = "occurrence/areaencounter_form.html"
    form_class = AreaEncounterForm
    success_url = "/"


class TaxonAreaEncounterCreateView(AreaEncounterCreateView):

    template_name = "occurrence/taxonareaencounter_form.html"
    form_class = TaxonAreaEncounterForm
    success_url = "/"


class CommunityAreaEncounterCreateView(AreaEncounterCreateView):

    template_name = "occurrence/communityareaencounter_form.html"
    form_class = CommunityAreaEncounterForm
    success_url = "/"
