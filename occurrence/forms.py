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
            # "encountered_on": shared_forms.DateTimeInput(),
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
                    # Div("code", css_class=THIRDS),
                    Div("name", css_class=HALF),
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
            # "encountered_on": shared_forms.DateTimeInput(),
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
                    Div("area_type", css_class=THIRDS),
                    Div("code", css_class=THIRDS),
                    Div("name", css_class=THIRDS),
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
                "File",
                Div(
                    Div('attachment', css_class=THIRDS),
                    Div('author', css_class=THIRDS),
                    Div('confidential', css_class=THIRDS),
                    css_class='row'
                ),
                Div(
                    Div('title', css_class="col col-12"),
                    css_class='row'
                ),
            ),
            ButtonHolder(
                Submit("submit",
                       "Submit",
                       css_class="button btn-block")
            )
        )


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
                    Div("survey_method", css_class=THIRDS),
                    Div("area_surveyed_m2", css_class=THIRDS),
                    Div("survey_duration_min", css_class=THIRDS),
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
            "soil_condition",
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
                    Div("good_percent", css_class=QUARTER),
                    Div("degraded_percent", css_class=QUARTER),
                    Div("completely_degraded_percent", css_class=QUARTER),
                    Div("soil_condition", css_class=QUARTER),
                    css_class='row'
                ),
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


class PlantCountForm(forms.ModelForm):
    """PlantCount Form."""

    class Meta:
        """Class options."""

        model = occ_models.PlantCount
        fields = [
            "encounter",
            "land_manager_present",
            "count_method",
            "count_accuracy",
            "count_subject",
            # Plant Count (Detailed)
            "no_alive_mature",
            "no_alive_juvenile",
            "no_alive_seedlings",
            "no_dead_mature",
            "no_dead_juvenile",
            "no_dead_seedlings",
            # Plant Count (Simple)
            "no_alive_simple",
            "no_dead_simple",
            # Quadrats
            "population_area_estimated_m2",
            "quadrats_present",
            "quadrats_details_attached",
            "no_quadrats_surveyed",
            "quadrat_area_individual_m2",
            "quadrat_area_total_m2",
            # Flowering
            "flowering_plants_percent",
            "clonal_present",
            "vegetative_present",
            "flowerbuds_present",
            "flowers_present",
            "immature_fruit_present",
            "ripe_fruit_present",
            "dehisced_fruit_present",
            "plant_condition",
            "comments",

            "count_method",
            "count_accuracy",
            "quadrats_present",
            "quadrats_details_attached",
            "flowering_plants_percent",
            "clonal_present",
            "vegetative_present",
            "flowerbuds_present",
            "flowers_present",
            "immature_fruit_present",
            "ripe_fruit_present",
            "dehisced_fruit_present",
            "plant_condition",
        ]
        widgets = {
            "encounter": occ_widgets.AreaEncounterWidget(),
        }

    def __init__(self, *args, **kwargs):
        """Customise form layout."""
        super(PlantCountForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Observation made during encounter",
                "encounter"
            ),
            Fieldset(
                "Plant count survey",
                Div(
                    Div("land_manager_present", css_class=QUARTER),
                    Div("count_method", css_class=QUARTER),
                    Div("count_accuracy", css_class=QUARTER),
                    Div("count_subject", css_class=QUARTER),
                    css_class="row"
                ),
            ),
            Fieldset(
                "Plant Count (Detailed)",
                Div(
                    Div("no_alive_mature", css_class=THIRDS),
                    Div("no_alive_juvenile", css_class=THIRDS),
                    Div("no_alive_seedlings", css_class=THIRDS),
                    Div("no_dead_mature", css_class=THIRDS),
                    Div("no_dead_juvenile", css_class=THIRDS),
                    Div("no_dead_seedlings", css_class=THIRDS),
                    css_class="row"
                ),
            ),
            Fieldset(
                "Plant Count (Simple)",
                Div(
                    Div("no_alive_simple", css_class=HALF),
                    Div("no_dead_simple", css_class=HALF),
                    css_class="row"
                ),
            ),
            Fieldset(
                "Quadrats",
                Div(
                    Div("quadrats_present", css_class=THIRDS),
                    Div("quadrats_details_attached", css_class=THIRDS),
                    Div("no_quadrats_surveyed", css_class=THIRDS),
                    css_class="row"
                ),
                Div(
                    Div("population_area_estimated_m2", css_class=THIRDS),
                    Div("quadrat_area_individual_m2", css_class=THIRDS),
                    Div("quadrat_area_total_m2", css_class=THIRDS),
                    css_class="row"
                ),
            ),
            Fieldset(
                "Flowering",
                Div(
                    Div("flowering_plants_percent", css_class=QUARTER),
                    Div("clonal_present", css_class=QUARTER),
                    Div("vegetative_present", css_class=QUARTER),
                    Div("flowerbuds_present", css_class=QUARTER),
                    css_class="row"
                ),
                Div(
                    Div("flowers_present", css_class=QUARTER),
                    Div("immature_fruit_present", css_class=QUARTER),
                    Div("ripe_fruit_present", css_class=QUARTER),
                    Div("dehisced_fruit_present", css_class=QUARTER),
                    css_class="row"
                ),
            ),
            Fieldset(
                "Plant condition",
                Div(
                    Div("plant_condition", css_class="col col-12"),
                    Div("comments", css_class="col col-12"),
                    css_class="row"
                ),
            ),
            ButtonHolder(
                Submit("submit",
                       "Submit",
                       css_class="button btn-block")
            )
        )


class VegetationClassificationForm(forms.ModelForm):
    """VegetationClassification Form."""

    class Meta:
        """Class options."""

        model = occ_models.VegetationClassification
        fields = (
            "encounter",
            "level1",
            "level2",
            "level3",
            "level4",
        )
        widgets = {
            "encounter": occ_widgets.AreaEncounterWidget(),
        }

    def __init__(self, *args, **kwargs):
        """Customise form layout."""
        super(VegetationClassificationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Observation made during encounter",
                "encounter"
            ),
            Fieldset(
                "Vegetation Classification",
                "level1",
                "level2",
                "level3",
                "level4",
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


class AnimalObservationForm(forms.ModelForm):
    """AnimalObservation Form."""

    class Meta:
        """Class options."""

        model = occ_models.AnimalObservation
        fields = (
            "encounter",
            "detection_method",
            "species_id_confidence",
            "maturity",
            "health",
            "cause_of_death",
            "distinctive_features",
            "actions_taken",
            "actions_required",
            "no_adult_male",
            "no_adult_female",
            "no_adult_unknown",
            "no_juvenile_male",
            "no_juvenile_female",
            "no_juvenile_unknown",
            "no_dependent_young_male",
            "no_dependent_young_female",
            "no_dependent_young_unknown",
            "observation_details",
            "secondary_signs",
        )
        widgets = {
            "encounter": occ_widgets.AreaEncounterWidget(),
        }

    def __init__(self, *args, **kwargs):
        """Customise form layout."""
        super(AnimalObservationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Observation made during encounter",
                "encounter"
            ),
            Fieldset(
                "Animal Observation",
                Div(
                    Div("detection_method", css_class=HALF),
                    Div("species_id_confidence", css_class=HALF),
                    css_class="row"
                ),
                Div(
                    Div("maturity", css_class=THIRDS),
                    Div("health", css_class=THIRDS),
                    Div("cause_of_death", css_class=THIRDS),
                    css_class="row"
                ),
                Div(
                    Div("distinctive_features", css_class=THIRDS),
                    Div("actions_taken", css_class=THIRDS),
                    Div("actions_required", css_class=THIRDS),
                    css_class="row"
                ),
                Div(
                    Div("observation_details", css_class=HALF),
                    Div("secondary_signs", css_class=HALF),
                    css_class="row"
                ),
            ),
            Fieldset(
                "Group Observation",
                Div(
                    Div("no_adult_male", css_class=THIRDS),
                    Div("no_adult_female", css_class=THIRDS),
                    Div("no_adult_unknown", css_class=THIRDS),

                    Div("no_juvenile_male", css_class=THIRDS),
                    Div("no_juvenile_female", css_class=THIRDS),
                    Div("no_juvenile_unknown", css_class=THIRDS),

                    Div("no_dependent_young_male", css_class=THIRDS),
                    Div("no_dependent_young_female", css_class=THIRDS),
                    Div("no_dependent_young_unknown", css_class=THIRDS),
                    css_class="row"
                ),
            ),
            ButtonHolder(
                Submit("submit",
                       "Submit",
                       css_class="button btn-block")
            )
        )


class PhysicalSampleForm(forms.ModelForm):
    """PhysicalSample Form."""

    class Meta:
        """Class options."""

        model = occ_models.PhysicalSample
        fields = (
            "encounter",
            "sample_type",
            "sample_label",
            "collector_id",
            "sample_destination",
            "permit_type",
            "permit_id",
        )
        widgets = {
            "encounter": occ_widgets.AreaEncounterWidget(),
        }

    def __init__(self, *args, **kwargs):
        """Customise form layout."""
        super(PhysicalSampleForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Observation made during encounter",
                "encounter"
            ),
            Fieldset(
                "Physical Sample or Specimen",
                Div(
                    Div("sample_type", css_class=THIRDS),
                    Div("sample_destination", css_class=THIRDS),
                    Div("permit_type", css_class=THIRDS),
                    css_class="row"
                ),
                Div(
                    Div("sample_label", css_class=THIRDS),
                    Div("collector_id", css_class=THIRDS),
                    Div("permit_id", css_class=THIRDS),
                    css_class="row"
                ),
            ),
            ButtonHolder(
                Submit("submit",
                       "Submit",
                       css_class="button btn-block")
            )
        )
