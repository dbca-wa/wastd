"""Django-Tables2 config for Occurrence data."""
import django_tables2 as tables
from django_tables2.utils import A
from occurrence.models import CommunityAreaEncounter, TaxonAreaEncounter


class TaxonAreaEncounterTable(tables.Table):
    """TaxonAreaEncounterTable config."""

    encounter = tables.LinkColumn(
        'admin:occurrence_taxonareaencounter_change',
        args=[A('pk'), ],
        orderable=False,
        empty_values=()
    )

    def render_encounter(self, record):
        """A link label for the encounter column."""
        return record.label

    class Meta:
        """Class opts."""

        model = TaxonAreaEncounter
        fields = ('encounter', 'description', 'encountered_on',
                  'area_type', 'code', 'name', 'accuracy',)


class CommunityAreaEncounterTable(tables.Table):
    """CommunityAreaEncounterTable config."""

    encounter = tables.LinkColumn(
        'admin:occurrence_communityareaencounter_change',
        args=[A('pk')],
        orderable=False,
        empty_values=()
    )

    def render_encounter(self, record):
        """A link label for the encounter column."""
        return record.label

    class Meta:
        """Class opts."""

        model = CommunityAreaEncounter
        fields = ('encounter', 'description', 'encountered_on',
                  'area_type', 'code', 'name', 'accuracy',)
