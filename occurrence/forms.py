# -*- coding: utf-8 -*-
"""Occurrence forms."""
from django import forms

from crispy_forms.layout import ButtonHolder, Fieldset, Layout, Submit
from crispy_forms.helper import FormHelper
from leaflet.forms.widgets import LeafletWidget

from wastd.users import widgets as usr_widgets
from taxonomy import widgets as tax_widgets
from occurrence import models as occ_models
from occurrence import widgets as occ_widgets
from shared.admin import S2ATTRS, LEAFLET_WIDGET_ATTRS, LEAFLET_SETTINGS, FORMFIELD_OVERRIDES  # noqa
from shared import forms as shared_forms


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
            "geolocation_capture_method",
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
            "geolocation_capture_method",
            "encountered_on",
            "encountered_by"
        )
        widgets = {
            "taxon": tax_widgets.TaxonWidget(),
            "geom": LeafletWidget(attrs=LEAFLET_WIDGET_ATTRS),
            "point": LeafletWidget(attrs=LEAFLET_WIDGET_ATTRS),
            "encountered_on": shared_forms.DateTimeInput(),
            "encountered_by": usr_widgets.UserWidget(),
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
                "geolocation_capture_method",
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
            "geolocation_capture_method",
            "encountered_on",
            "encountered_by"
        )
        widgets = {
            "community": tax_widgets.CommunityWidget(),
            "geom": LeafletWidget(attrs=LEAFLET_WIDGET_ATTRS),
            "point": LeafletWidget(attrs=LEAFLET_WIDGET_ATTRS),
            "encountered_on": shared_forms.DateTimeInput(),
            "encountered_by": usr_widgets.UserWidget(),
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
                "geolocation_capture_method",
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
class AssociatedSpeciesForm(forms.ModelForm):
    """Associated Species Form."""

    class Meta:
        """Class options."""

        model = occ_models.AssociatedSpecies
        fields = ("encounter", "taxon",)
        widgets = {
            "encounter": occ_widgets.AreaEncounterWidget(),
            "taxon": tax_widgets.TaxonWidget(),
        }

    def __init__(self, *args, **kwargs):
        """Customise form layout."""
        super(AssociatedSpeciesForm, self).__init__(*args, **kwargs)
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


class FireHistoryForm(forms.ModelForm):
    """Fire History Form."""

    class Meta:
        """Class options."""

        model = occ_models.FireHistory
        fields = (
            "encounter",
            "last_fire_date",
            "fire_intensity"
        )
        widgets = {
            "encounter": occ_widgets.AreaEncounterWidget(),
            "last_fire_date": shared_forms.DateInput(),
        }

    def __init__(self, *args, **kwargs):
        """Customise form layout."""
        super(FireHistoryForm, self).__init__(*args, **kwargs)
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


class FileAttachmentForm(forms.ModelForm):
    """FileAttachment Form."""

    class Meta:
        """Class options."""

        model = occ_models.FileAttachment
        fields = (
            "encounter",
            "attachment",
            "title",
            "author",
            "confidential"
        )
        widgets = {
            "encounter": occ_widgets.AreaEncounterWidget(),
            "author": usr_widgets.UserWidget(),
        }

    def __init__(self, *args, **kwargs):
        """Customise form layout."""
        super(FileAttachmentForm, self).__init__(*args, **kwargs)
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


class AreaAssessmentForm(forms.ModelForm):
    """AreaAssessment Form."""

    class Meta:
        """Class options."""

        model = occ_models.AreaAssessment
        fields = (
            "encounter",
            "survey_type",
            "area_surveyed_m2",
            "survey_duration_min",
        )
        widgets = {
            "encounter": occ_widgets.AreaEncounterWidget(),
        }

    def __init__(self, *args, **kwargs):
        """Customise form layout."""
        super(AreaAssessmentForm, self).__init__(*args, **kwargs)
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
