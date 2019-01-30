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
from taxonomy.models import Taxon

# ModelForms
from .forms import (AreaEncounterForm, TaxonAreaEncounterForm, CommunityAreaEncounterForm)

# select2 forms
# from .admin import (AreaForm, TaxonAreaForm, CommunityAreaForm)


class AreaEncounterCreateView(CreateView):
    """Create view for AreaEncounter."""

    template_name = "occurrence/areaencounter_form.html"
    form_class = AreaEncounterForm
    success_url = "/"  # default: form model's get_absolute_url()


class TaxonAreaEncounterCreateView(AreaEncounterCreateView):
    """Create view for TaxonAreaEncounter."""

    template_name = "occurrence/taxonareaencounter_form.html"
    form_class = TaxonAreaEncounterForm
    success_url = "/"

    def get_initial(self):
        """Initial form values."""
        initial = dict()
        if "name_id" in self.kwargs:
            initial['taxon'] = Taxon.objects.get(name_id=self.kwargs["name_id"])
        if "area_code" in self.kwargs:
            initial['code'] = self.kwargs["area_code"]
        return initial


class CommunityAreaEncounterCreateView(AreaEncounterCreateView):
    """Create view for CommunityAreaEncounter."""

    template_name = "occurrence/communityareaencounter_form.html"
    form_class = CommunityAreaEncounterForm
    success_url = "/"
