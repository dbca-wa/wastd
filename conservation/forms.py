# -*- coding: utf-8 -*-
"""Conservation forms."""

from django import forms
from django.contrib.contenttypes.forms import generic_inlineformset_factory
from django.contrib.admin import widgets as admin_widgets  # noqa
from django.utils.translation import ugettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Fieldset, Layout, Submit, Div
from leaflet.forms.widgets import LeafletWidget
from django_select2.forms import ModelSelect2Widget, ModelSelect2MultipleWidget  # noqa

from wastd.users import widgets as usr_widgets
from conservation import models as cons_models
from conservation import widgets as cons_widgets
from taxonomy import widgets as tax_widgets
from shared.admin import LEAFLET_SETTINGS
from shared import forms as shared_forms


class ConservationThreatForm(forms.ModelForm):
    """Common form for ConservationThreat."""

    class Meta:
        """Class options."""

        model = cons_models.ConservationThreat
        fields = (
            "taxa",
            "communities",
            "document",
            "occurrence_area_code",
            "target_area",
            "category",
            "cause",
            "encountered_by",
            "encountered_on",
            "area_affected_percent",
            "current_impact",
            "potential_impact",
            "potential_onset",
        )
        widgets = {
            'taxa': tax_widgets.TaxonMultipleWidget(),
            'communities': tax_widgets.CommunityMultipleWidget(),
            'document': cons_widgets.DocumentWidget(),
            'target_area': LeafletWidget(attrs=LEAFLET_SETTINGS),
            'category': cons_widgets.ConservationThreatCategoryWidget(),
            "encountered_on": shared_forms.DateTimeInput(),
            "encountered_by": usr_widgets.UserWidget(),
        }

    def __init__(self, *args, **kwargs):
        """Customise form layout."""
        super(ConservationThreatForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Threat affiliations',
                'taxa',
                'communities',
                'document',
                'target_area',
                'occurrence_area_code',
            ),
            Fieldset(
                'Threat',
                Div(
                    Div('encountered_on', css_class="col col-lg-6 col-md-6 col-sm-12 col-12"),
                    Div('encountered_by', css_class="col col-lg-6 col-md-6 col-sm-12 col-12"),
                    css_class='row'
                ),
                Div(
                    Div('area_affected_percent', css_class="col col-lg-3 col-md-6 col-sm-12 col-12"),
                    Div('current_impact', css_class="col col-lg-3 col-md-6 col-sm-12 col-12"),
                    Div('potential_impact', css_class="col col-lg-3 col-md-6 col-sm-12 col-12"),
                    Div('potential_onset', css_class="col col-lg-3 col-md-6 col-sm-12 col-12"),
                    css_class='row'
                ),
                Div(Div('category', css_class="col col-12"), css_class='row'),
                Div(Div('cause', css_class="col col-12"), css_class='row'),
            ),
            ButtonHolder(
                Submit('submit', 'Submit', css_class='button white')
            )
        )


class ConservationActionForm(forms.ModelForm):
    """Common form for ConservationAction."""

    class Meta:
        """Class options."""

        model = cons_models.ConservationAction
        fields = (
            "taxa",
            "communities",
            "document",
            "occurrence_area_code",
            "target_area",
            "category",
            "instructions",
            "implementation_notes",
            "completion_date",
            "expenditure",
            # "attachments"
        )
        widgets = {
            'taxa': tax_widgets.TaxonMultipleWidget(),
            'communities': tax_widgets.CommunityMultipleWidget(),
            'document': cons_widgets.DocumentWidget(),
            'target_area': LeafletWidget(attrs=LEAFLET_SETTINGS),
            'category': cons_widgets.ConservationActionCategoryWidget(),
            'completion_date': shared_forms.DateInput(),
        }

    def __init__(self, *args, **kwargs):
        """Customise form layout."""
        super(ConservationActionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Action affiliations',
                'taxa',
                'communities',
                'document',
                'target_area',
                'occurrence_area_code',
            ),
            Fieldset(
                'Task',
                'category',
                'instructions',
            ),
            Fieldset(
                'Implementation',
                'implementation_notes',
                Div(
                    Div('completion_date', css_class="col col-lg-6 col-md-6 col-sm-12 col-12"),
                    Div('expenditure', css_class="col col-lg-6 col-md-6 col-sm-12 col-12"),
                    css_class='row'
                ),
            ),
            ButtonHolder(
                Submit('submit', 'Submit', css_class='button white')
            )
        )


class ConservationActivityForm(forms.ModelForm):
    """Common form for ConservationActivity."""

    class Meta:
        """Class options."""

        model = cons_models.ConservationActivity
        fields = (
            "conservation_action",
            "implementation_notes",
            "completion_date",
            "expenditure",
            # "attachments"
        )
        widgets = {
            'conservation_action': cons_widgets.ConservationActionWidget(),
            'completion_date': shared_forms.DateInput(),
        }

    def __init__(self, *args, **kwargs):
        """Customise form layout."""
        super(ConservationActivityForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Task',
                'conservation_action',
            ),
            Fieldset(
                'Implementation',
                'implementation_notes',
                'completion_date',
                'expenditure',
                # 'attachments'
            ),
            ButtonHolder(
                Submit('submit', 'Submit', css_class='button white')
            )
        )


class TaxonConservationListingForm(forms.ModelForm):
    """Form for Taxon conservation listing (Gazettal)."""

    category = forms.ModelMultipleChoiceField(
        queryset=cons_models.ConservationCategory.objects.filter(
            conservation_list__scope_species=True,
            conservation_list__scope_wa=True,
            conservation_list__active_to__isnull=True
        ).prefetch_related(
            'conservation_list'
        ).order_by(
            "conservation_list__code", "rank"
        ),
        label=_("Conservation Categories"),
        widget=ModelSelect2MultipleWidget(
            model=cons_models.ConservationCategory,
            queryset=cons_models.ConservationCategory.objects.filter(
                conservation_list__scope_species=True,
                conservation_list__scope_wa=True,
                conservation_list__active_to__isnull=True
            ).prefetch_related(
                'conservation_list'
            ).order_by(
                "conservation_list__code", "rank"
            ),
            search_fields=[
                'conservation_list__code__icontains',
                'code__icontains',
                'label__icontains',
                'description__icontains'
            ],
            # dependent_fields={'conservation_list__code': 'scope'},
            max_results=500,
        )
    )

    criteria = forms.ModelMultipleChoiceField(
        queryset=cons_models.ConservationCriterion.objects.filter(
            conservation_list__scope_species=True,
            conservation_list__scope_wa=True,
            conservation_list__active_to__isnull=True
        ).prefetch_related(
            'conservation_list'
        ).order_by(
            "conservation_list__code", "rank"
        ),
        label=_("Conservation Criteria"),
        widget=ModelSelect2MultipleWidget(
            model=cons_models.ConservationCriterion,
            queryset=cons_models.ConservationCriterion.objects.filter(
                conservation_list__scope_species=True,
                conservation_list__scope_wa=True,
                conservation_list__active_to__isnull=True
            ).prefetch_related(
                'conservation_list'
            ).order_by(
                "conservation_list__code", "rank"
            ),
            search_fields=[
                'conservation_list__code__icontains',
                'code__icontains',
                'label__icontains',
                'description__icontains'
            ],
            # dependent_fields={'conservation_list__code': 'scope'},
            max_results=500,
        )
    )

    class Meta:
        """Class options."""

        model = cons_models.TaxonGazettal
        fields = (
            "taxon",
            # "scope",
            "category",
            "criteria",
            "proposed_on",
            "last_reviewed_on",
            "review_due",
            "comments"
        )
        widgets = {
            'taxon': tax_widgets.TaxonWidget(),
            'proposed_on': shared_forms.DateInput(),
            'last_reviewed_on': shared_forms.DateInput(),
            'review_due': shared_forms.DateInput(),
        }

    def __init__(self, *args, **kwargs):
        """Customise form layout."""
        super(TaxonConservationListingForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(

            Fieldset(
                "Conservation Listing",
                Div(
                    Div("taxon", css_class="col col-12"),
                    css_class='row'
                ),
                Div(
                    # Div('scope', css_class="col col-lg-4 col-md-12 col-12"),
                    Div('category', css_class="col col-lg-6 col-md-6 col-sm-12 col-12"),
                    Div('criteria', css_class="col col-lg-6 col-md-6 col-sm-12 col-12"),
                    css_class='row'
                ),
            ),
            Fieldset(
                "Approval process",
                Div(
                    Div("proposed_on", css_class="col col-md-4 col-12"),
                    Div("last_reviewed_on", css_class="col col-md-4 col-12"),
                    Div("review_due", css_class="col col-md-4 col-12"),
                    css_class='row'
                ),
                "comments",
            ),
            ButtonHolder(
                Submit('submit', 'Submit', css_class='button white')
            )
        )


class CommunityConservationListingForm(forms.ModelForm):
    """Form for Community conservation listing (Gazettal)."""

    category = forms.ModelMultipleChoiceField(
        queryset=cons_models.ConservationCategory.objects.filter(
            conservation_list__scope_communities=True,
            conservation_list__scope_wa=True,
            conservation_list__active_to__isnull=True
        ).prefetch_related(
            'conservation_list'
        ).order_by(
            "conservation_list__code", "rank"
        ),
        label=_("Conservation Categories"),
        widget=ModelSelect2MultipleWidget(
            model=cons_models.ConservationCategory,
            queryset=cons_models.ConservationCategory.objects.filter(
                conservation_list__scope_communities=True,
                conservation_list__scope_wa=True,
                conservation_list__active_to__isnull=True
            ).prefetch_related(
                'conservation_list'
            ).order_by(
                "conservation_list__code", "rank"
            ),
            search_fields=[
                'conservation_list__code__icontains',
                'code__icontains',
                'label__icontains',
                'description__icontains'
            ],
            # dependent_fields={'conservation_list__code': 'scope'},
            max_results=500,
        )
    )

    criteria = forms.ModelMultipleChoiceField(
        queryset=cons_models.ConservationCriterion.objects.filter(
            conservation_list__scope_communities=True,
            conservation_list__scope_wa=True,
            conservation_list__active_to__isnull=True
        ).prefetch_related(
            'conservation_list'
        ).order_by(
            "conservation_list__code", "rank"
        ),
        label=_("Conservation Criteria"),
        widget=ModelSelect2MultipleWidget(
            model=cons_models.ConservationCriterion,
            queryset=cons_models.ConservationCriterion.objects.filter(
                conservation_list__scope_communities=True,
                conservation_list__scope_wa=True,
                conservation_list__active_to__isnull=True
            ).prefetch_related(
                'conservation_list'
            ).order_by(
                "conservation_list__code", "rank"
            ),
            search_fields=[
                'conservation_list__code__icontains',
                'code__icontains',
                'label__icontains',
                'description__icontains'
            ],
            # dependent_fields={'conservation_list__code': 'scope'},
            max_results=500,
        )
    )

    class Meta:
        """Class options."""

        model = cons_models.CommunityGazettal
        fields = (
            "community",
            # "scope",
            "category",
            "criteria",
            "proposed_on",
            "last_reviewed_on",
            "review_due",
            "comments"
        )
        widgets = {
            'community': tax_widgets.CommunityWidget(),
            'proposed_on': shared_forms.DateInput(),
            'last_reviewed_on': shared_forms.DateInput(),
            'review_due': shared_forms.DateInput(),
        }

    def __init__(self, *args, **kwargs):
        """Customise form layout."""
        super(CommunityConservationListingForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Conservation Listing",
                Div(
                    Div("community", css_class="col col-12"),
                    css_class='row'
                ),
                Div(
                    # Div('scope', css_class="col col-lg-4 col-md-12 col-12"),
                    Div('category', css_class="col col-lg-6 col-md-6 col-sm-12 col-12"),
                    Div('criteria', css_class="col col-lg-6 col-md-6 col-sm-12 col-12"),
                    css_class='row'
                ),
            ),
            Fieldset(
                "Approval process",
                Div(
                    Div("proposed_on", css_class="col col-md-4 col-12"),
                    Div("last_reviewed_on", css_class="col col-md-4 col-12"),
                    Div("review_due", css_class="col col-md-4 col-12"),
                    css_class='row'
                ),
                "comments",
            ),
            ButtonHolder(
                Submit('submit', 'Submit', css_class='button white')
            )
        )


class DocumentForm(forms.ModelForm):
    """Form for Documents."""

    def __init__(self, *args, **kwargs):
        """Customise form layout."""
        super(DocumentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Document',
                Div(
                    Div('document_type', css_class="col-3 col-sm-12"),
                    Div('title', css_class="col-9 col-sm-12"),
                    css_class='row'
                ),
                "comments",
            ),
            Fieldset(
                'Relations',
                "taxa",
                "communities",
                "team",
            ),
            Fieldset(
                'Dates',
                Div(
                    Div('effective_from', css_class="col col-lg-6 col-md-6 col-sm-12 col-12"),
                    Div('effective_to', css_class="col col-lg-6 col-md-6 col-sm-12 col-12"),
                    css_class='row'
                ),
                Div(
                    Div('last_reviewed_on', css_class="col col-lg-6 col-md-6 col-sm-12 col-12"),
                    Div('review_due', css_class="col col-lg-6 col-md-6 col-sm-12 col-12"),
                    css_class='row'
                ),
                Div(
                    Div('effective_from_commonwealth', css_class="col col-lg-6 col-md-6 col-sm-12 col-12"),
                    Div('effective_to_commonwealth', css_class="col col-lg-6 col-md-6 col-sm-12 col-12"),
                    css_class='row'
                ),
            ),
            ButtonHolder(
                Submit('submit', 'Submit', css_class='button white')
            )
        )

    class Meta:
        """Class options."""

        model = cons_models.Document
        fields = (
            "document_type",
            "title",
            "taxa",
            "communities",
            "team",
            "effective_from",
            "effective_to",
            "effective_from_commonwealth",
            "effective_to_commonwealth",
            "last_reviewed_on",
            "review_due",
            "comments",
        )
        widgets = {
            'taxa': tax_widgets.TaxonMultipleWidget(),
            'communities': tax_widgets.CommunityMultipleWidget(),
            'team': usr_widgets.UserMultipleWidget(),
            'effective_from': shared_forms.DateTimeInput(),  # widgets.AdminSplitDateTime(),
            'effective_to': shared_forms.DateTimeInput(),
            'effective_from_commonwealth': shared_forms.DateTimeInput(),
            'effective_to_commonwealth': shared_forms.DateTimeInput(),
            'last_reviewed_on': shared_forms.DateTimeInput(),
            'review_due': shared_forms.DateTimeInput(),
        }


class FileAttachmentForm(forms.ModelForm):
    """A model form for FileAttachments."""

    class Meta:
        """Class options."""

        model = cons_models.FileAttachment
        exclude = ()
        widgets = {
            "author": usr_widgets.UserWidget(),
        }

FileAttachmentFormSet = generic_inlineformset_factory(
    cons_models.FileAttachment, form=FileAttachmentForm, extra=1
)


class FileAttachmentFormSetHelper(FormHelper):
    """FileAttachmentFormSetHelper."""

    def __init__(self, *args, **kwargs):
        """Init."""
        super(FileAttachmentFormSetHelper, self).__init__(*args, **kwargs)
        self.form_method = 'post'
        self.layout = Layout(
            Fieldset(
                'File attachment',
                Div(
                    Div('attachment', css_class="col col-lg-3 col-md-6 col-12"),
                    Div('author', css_class="col col-lg-3 col-md-6 col-12"),
                    Div('current', css_class="col col-lg-3 col-md-6 col-12"),
                    Div('confidential', css_class="col col-lg-3 col-md-6 col-12"),
                    css_class='row'
                ),
                'title'
            ),
        )
        self.render_required_fields = True
