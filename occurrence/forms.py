# -*- coding: utf-8 -*-
"""Occurrence forms."""

from django import forms
from django.contrib.auth import get_user_model
from django_select2.forms import ModelSelect2Widget

from crispy_forms.layout import ButtonHolder, Fieldset, Layout, Submit
from crispy_forms.helper import FormHelper
from leaflet.forms.widgets import LeafletWidget

from taxonomy.models import Community, Taxon
from occurrence import models as occ_models
from shared.admin import S2ATTRS, LEAFLET_WIDGET_ATTRS, LEAFLET_SETTINGS, FORMFIELD_OVERRIDES  # noqa
from shared.forms import DateInput, DateTimeInput
from shared import filters as shared_filters
# from wastd.users.models import User


class AreaEncounterForm(forms.ModelForm):
    """Common form for AreaEncounter."""

    class Meta:
        """Class options."""

        model = occ_models.AreaEncounter
        formfield_overrides = FORMFIELD_OVERRIDES
        fields = (
            "area_type",
            "code",
            "name",
            "description",
            "geom",
            "accuracy",
            "encountered_on",
            "encountered_by"
        )
        # widgets = {"geom": LeafletWidget(attrs=LEAFLET_SETTINGS)}


class TaxonAreaEncounterForm(AreaEncounterForm):
    """Form for TaxonAreaEncounter."""

    class Meta:
        """Class options."""

        model = occ_models.TaxonAreaEncounter
        formfield_overrides = FORMFIELD_OVERRIDES
        fields = (
            "taxon",
            "area_type",
            "code",
            "name",
            "description",
            "geom",
            "point",
            "accuracy",
            "encountered_on",
            "encountered_by"
        )
        widgets = {
            "taxon": shared_filters.TaxonWidget(),
            "geom": LeafletWidget(attrs=LEAFLET_WIDGET_ATTRS),
            "point": LeafletWidget(attrs=LEAFLET_WIDGET_ATTRS),
            "encountered_on": DateTimeInput(),
            "encountered_by": shared_filters.UserWidget(),
        }

    def __init__(self, *args, **kwargs):
        """Customise form layout."""
        super(TaxonAreaEncounterForm, self).__init__(*args, **kwargs)
        self.fields["area_type"].choices = occ_models.AreaEncounter.TAXON_AREA_TYPES
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Who",
                "encountered_by",
            ),
            Fieldset(
                "When",
                "encountered_on",
            ),
            Fieldset(
                "What",
                "taxon",
                "description",
            ),
            Fieldset(
                "Where",
                "area_type",
                "code",
                "geom",
                "point",
                "accuracy",
            ),
            ButtonHolder(
                Submit("submit",
                       "Submit",
                       css_class="button white")
            )
        )


class CommunityAreaEncounterForm(AreaEncounterForm):
    """Form for CommunityAreaEncounter."""

    class Meta:
        """Class options."""

        model = occ_models.CommunityAreaEncounter
        fields = (
            "community",
            "area_type",
            "code",
            "name",
            "description",
            "geom",
            "point",
            "accuracy",
            "encountered_on",
            "encountered_by"
        )
        widgets = {
            "community": ModelSelect2Widget(
                model=Community,
                search_fields=[
                    "name__icontains",
                    "code__icontains",
                ]
            ),
            "geom": LeafletWidget(attrs=LEAFLET_WIDGET_ATTRS),
            "point": LeafletWidget(attrs=LEAFLET_WIDGET_ATTRS),
            "encountered_on": DateTimeInput(),
            "encountered_by": shared_filters.UserWidget(),
        }

    def __init__(self, *args, **kwargs):
        """Customise form layout."""
        super(CommunityAreaEncounterForm, self).__init__(*args, **kwargs)
        self.fields["area_type"].choices = occ_models.AreaEncounter.COMMUNITY_AREA_TYPES
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Who",
                "encountered_by",
            ),
            Fieldset(
                "When",
                "encountered_on",
            ),
            Fieldset(
                "What",
                "community",
                "description",
            ),
            Fieldset(
                "Where",
                "area_type",
                "code",
                "geom",
                "point",
                "accuracy",
            ),
            ButtonHolder(
                Submit("submit",
                       "Submit",
                       css_class="button white")
            )
        )


# ----------------------------------------------------------------------------#
# ObservationGroup forms
#
class AssociatedSpeciesObservationForm(forms.ModelForm):
    """Associated Species Observation Form."""

    class Meta:
        """Class options."""

        model = occ_models.AssociatedSpeciesObservation
        fields = ("encounter", "taxon",)
        widgets = {
            "encounter": ModelSelect2Widget(
                model=occ_models.AreaEncounter,
                search_fields=[
                    "code",
                    "name",
                    "area_type",
                ],
                attrs={"size": 80}
            ),
            "taxon": ModelSelect2Widget(
                model=Taxon,
                search_fields=[
                    "taxonomic_name__icontains",
                    "vernacular_names__icontains",
                    "field_code__icontains",
                ],
                attrs={"size": 80}
            ),
        }

    def __init__(self, *args, **kwargs):
        """Customise form layout."""
        super(AssociatedSpeciesObservationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Observation made during encounter",
                "encounter"
            ),
            Fieldset(
                "Associated Species",
                "taxon",
            ),
            ButtonHolder(
                Submit("submit",
                       "Submit",
                       css_class="button white")
            )
        )


class FireHistoryObservationForm(forms.ModelForm):
    """Fire History Observation Form."""

    class Meta:
        """Class options."""

        model = occ_models.FireHistoryObservation
        fields = (
            "encounter",
            "last_fire_date",
            "fire_intensity"
        )
        widgets = {
            "encounter": ModelSelect2Widget(
                model=occ_models.AreaEncounter,
                search_fields=[
                    "code",
                    "name",
                    "area_type",
                ],
                attrs={"size": 80}
            ),
            "last_fire_date": DateInput(),
        }

    def __init__(self, *args, **kwargs):
        """Customise form layout."""
        super(FireHistoryObservationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Observation made during encounter",
                "encounter"
            ),
            Fieldset(
                "Fire History",
                "last_fire_date",
                "fire_intensity"
            ),
            ButtonHolder(
                Submit("submit",
                       "Submit",
                       css_class="button white")
            )
        )


class FileAttachmentObservationForm(forms.ModelForm):
    """FileAttachmentObservation Form."""

    class Meta:
        """Class options."""

        model = occ_models.FileAttachmentObservation
        fields = (
            "encounter",
            "attachment",
            "title",
            "author",
            "confidential"
        )
        widgets = {
            "encounter": ModelSelect2Widget(
                model=occ_models.AreaEncounter,
                search_fields=[
                    "code",
                    "name",
                    "area_type",
                ],
                attrs={"size": 80}
            ),
            "author": ModelSelect2Widget(
                model=get_user_model(),
                search_fields=[
                    "name__icontains",
                    "username__icontains",
                    "role__icontains",
                    "email__icontains"
                ]
            ),
        }

    def __init__(self, *args, **kwargs):
        """Customise form layout."""
        super(FileAttachmentObservationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Observation made during encounter",
                "encounter"
            ),
            Fieldset(
                "File attachment",
                "attachment",
                "title",
                "author",
                "confidential"
            ),
            ButtonHolder(
                Submit("submit",
                       "Submit",
                       css_class="button white")
            )
        )


class AreaAssessmentObservationForm(forms.ModelForm):
    """AreaAssessmentObservation Form."""

    class Meta:
        """Class options."""

        model = occ_models.AreaAssessmentObservation
        fields = (
            "encounter",
            "survey_type",
            "area_surveyed_m2",
            "survey_duration_min",
        )
        widgets = {
            "encounter": ModelSelect2Widget(
                model=occ_models.AreaEncounter,
                search_fields=[
                    "code",
                    "name",
                    "area_type",
                ],
                attrs={"size": 80}
            ),
        }

    def __init__(self, *args, **kwargs):
        """Customise form layout."""
        super(AreaAssessmentObservationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Observation made during encounter",
                "encounter"
            ),
            Fieldset(
                "Survey Effort",
                "survey_type",
                "area_surveyed_m2",
                "survey_duration_min",
            ),
            ButtonHolder(
                Submit("submit",
                       "Submit",
                       css_class="button white")
            )
        )
