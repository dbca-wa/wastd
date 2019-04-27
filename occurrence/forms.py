# -*- coding: utf-8 -*-
"""Occurrence forms."""
from django import forms

from crispy_forms.layout import ButtonHolder, Fieldset, Layout, Submit, Div
from crispy_forms.helper import FormHelper
from leaflet.forms.widgets import LeafletWidget

from wastd.users import widgets as usr_widgets
from taxonomy import widgets as tax_widgets
from occurrence import models as occ_models
from occurrence import widgets as occ_widgets
from shared.admin import S2ATTRS, LEAFLET_WIDGET_ATTRS, LEAFLET_SETTINGS, FORMFIELD_OVERRIDES  # noqa
from shared import forms as shared_forms

HALF = "col col-lg-6 col-md-6 col-sm-12 col-12"
THIRDS = "col col-lg-4 col-md-4 col-sm-6 col-12"
QUARTER = "col col-lg-3 col-md-3 col-sm-6 col-12"


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
            "encounter_type",
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
                "Encounter",
                Div(
                    Div("encountered_on", css_class=THIRDS),
                    Div("encountered_by", css_class=THIRDS),
                    Div("encounter_type", css_class=THIRDS),
                    css_class="row"
                ),
            ),
            Fieldset(
                "Subject",
                Div(
                    Div("taxon", css_class="col col-12"),
                    Div("description", css_class="col col-12"),
                    css_class="row"
                ),
            ),
            Fieldset(
                "Location",
                Div(
                    Div("area_type", css_class=HALF),
                    Div("code", css_class=HALF),
                    css_class="row"
                ),
                Div(
                    Div("geom", css_class=HALF),
                    Div("point", css_class=HALF),
                    css_class="row"
                ),
                Div(
                    Div("geolocation_capture_method", css_class=HALF),
                    Div("accuracy", css_class=HALF),
                    css_class="row"
                ),
            ),
            ButtonHolder(
                Submit("submit",
                       "Submit",
                       css_class="button white btn-block")
            )
        )


class CommunityAreaEncounterForm(AreaEncounterForm):
    """Form for CommunityAreaEncounter."""

    class Meta:
        """Class options."""

        model = occ_models.CommunityAreaEncounter
        fields = (
            "community",
            "encounter_type",
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
                "Encounter",
                Div(
                    Div("encountered_on", css_class=THIRDS),
                    Div("encountered_by", css_class=THIRDS),
                    Div("encounter_type", css_class=THIRDS),
                    css_class="row"
                ),
            ),
            Fieldset(
                "Subject",
                Div(
                    Div("community", css_class="col col-12"),
                    Div("description", css_class="col col-12"),
                    css_class="row"
                ),
            ),
            Fieldset(
                "Location",
                Div(
                    Div("area_type", css_class=HALF),
                    Div("code", css_class=HALF),
                    css_class="row"
                ),
                Div(
                    Div("geom", css_class=HALF),
                    Div("point", css_class=HALF),
                    css_class="row"
                ),
                Div(
                    Div("geolocation_capture_method", css_class=HALF),
                    Div("accuracy", css_class=HALF),
                    css_class="row"
                ),
            ),
            ButtonHolder(
                Submit("submit",
                       "Submit",
                       css_class="button white btn-block")
            )
        )


# ----------------------------------------------------------------------------#
# ObservationGroup forms
#
class HabitatCompositionForm(forms.ModelForm):
    """HabitatComposition Form."""

    class Meta:
        """Class options."""

        model = occ_models.HabitatComposition
        fields = (
            "encounter",
            "landform",
            "rock_type",
            "loose_rock_percent",
            "soil_type",
            "soil_colour",
            "drainage",
        )
        widgets = {
            "encounter": occ_widgets.AreaEncounterWidget(),
            # "taxon": tax_widgets.TaxonWidget(),
        }

    def __init__(self, *args, **kwargs):
        """Customise form layout."""
        super(HabitatCompositionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Observation made during encounter",
                "encounter"
            ),
            Fieldset(
                "Habitat Composition",
                Div(
                    Div("landform", css_class=THIRDS),
                    Div("rock_type", css_class=THIRDS),
                    Div("loose_rock_percent", css_class=THIRDS),
                    css_class="row"
                ),
                Div(
                    Div("soil_type", css_class=THIRDS),
                    Div("soil_colour", css_class=THIRDS),
                    Div("drainage", css_class=THIRDS),
                    css_class="row"
                ),
            ),
            ButtonHolder(
                Submit("submit",
                       "Submit",
                       css_class="button btn-block")
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
            "survey_method",
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
                Div(
                    Div("survey_type", css_class=QUARTER),
                    Div("survey_method", css_class=QUARTER),
                    Div("area_surveyed_m2", css_class=QUARTER),
                    Div("survey_duration_min", css_class=QUARTER),
                    css_class='row'
                ),
            ),
            ButtonHolder(
                Submit("submit",
                       "Submit",
                       css_class="button btn-block")
            )
        )


class HabitatConditionForm(forms.ModelForm):
    """HabitatCondition Form."""

    class Meta:
        """Class options."""

        model = occ_models.HabitatCondition
        fields = (
            "encounter",
            "pristine_percent",
            "excellent_percent",
            "very_good_percent",
            "good_percent",
            "degraded_percent",
            "completely_degraded_percent",
        )
        widgets = {
            "encounter": occ_widgets.AreaEncounterWidget(),
        }

    def __init__(self, *args, **kwargs):
        """Customise form layout."""
        super(HabitatConditionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Observation made during encounter",
                "encounter"
            ),
            Fieldset(
                "Occurrence Condition",
                Div(
                    Div("pristine_percent", css_class=THIRDS),
                    Div("excellent_percent", css_class=THIRDS),
                    Div("very_good_percent", css_class=THIRDS),
                    Div("good_percent", css_class=THIRDS),
                    Div("degraded_percent", css_class=THIRDS),
                    Div("completely_degraded_percent", css_class=THIRDS),
                    css_class='row'
                ),
            ),
            ButtonHolder(
                Submit("submit",
                       "Submit",
                       css_class="button btn-block")
            )
        )


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
                       css_class="button btn-block")
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
                "Evidence of past fire",
                Div(
                    Div("last_fire_date", css_class=HALF),
                    Div("fire_intensity", css_class=HALF),
                    css_class="row"
                ),
            ),
            ButtonHolder(
                Submit("submit",
                       "Submit",
                       css_class="button btn-block")
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
                Div(
                    Div('attachment', css_class=THIRDS),
                    Div('author', css_class=THIRDS),
                    Div('confidential', css_class=THIRDS),
                    css_class='row'
                ),
                'title'
            ),
            ButtonHolder(
                Submit("submit",
                       "Submit",
                       css_class="button btn-block")
            )
        )
