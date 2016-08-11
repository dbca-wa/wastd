# -*- coding: utf-8 -*-
"""
    Opportunistic sighting of stranded/encountered dead or injured wildlife.

    Species use a local name list, but should lookup a webservice.
    This Observation is generic for all species. Other Models can FK this Model
    to add species-specific measurements.

    Observer name / address / phone / email is captured with observer as system
    user.

    The combination of species and health determines subsequent measurements
    and actions:

    * [turtle, dugong, cetacean] damage observation
    * [turtle, dugong, cetacean] distinguished features
    * [taxon] morphometrics
    * [flipper, pit, sat] tag observation
    * disposal actions

"""
from __future__ import unicode_literals, absolute_import

# from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.gis.db import models as geo_models
from django.core.urlresolvers import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from polymorphic.models import PolymorphicModel
from django_fsm import FSMField, transition
import urllib

from wastd.users.models import User


# Encounter models -----------------------------------------------------------#
@python_2_unicode_compatible
class Encounter(PolymorphicModel, geo_models.Model):
    """The base Encounter class knows when, where, who.

    When: Datetime of encounter, stored in UTC, entered and displayed in local
    timezome.
    Where: Point in WGS84.
    Who: The observer has to be a registered system user.
    """
    STATUS_NEW = 'new'
    STATUS_PROOFREAD = 'proofread'
    STATUS_CURATED = 'curated'
    STATUS_PUBLISHED = 'published'

    STATUS_CHOICES = (
        (STATUS_NEW, _("New")),
        (STATUS_PROOFREAD, _("Proofread")),
        (STATUS_CURATED, _("Curated")),
        (STATUS_PUBLISHED, _("Published"))
        )

    STATUS_LABELS = {
        STATUS_NEW: "danger",
        STATUS_PROOFREAD: "warning",
        STATUS_CURATED: "info",
        STATUS_PUBLISHED: "success"
        }

    LOCATION_ACCURACY_CHOICES = (
        ("10m", "GPS reading at exact location (+-10m)"),
        ("1km", "GPS reading in general area (+-1km)"),
        ("1nm", "Map reference (+-1nm)"),
        ("online-map", "Drawn on online map"),
        ("na", "Location not provided"), )

    status = FSMField(
        default=STATUS_NEW,
        choices=STATUS_CHOICES,
        verbose_name=_("QA Status"))

    when = models.DateTimeField(
        verbose_name=_("Observed on"),
        help_text=_("The observation datetime, shown here as local time, "
                    "stored as UTC."))

    where = geo_models.PointField(
        srid=4326,
        verbose_name=_("Observed at"),
        help_text=_("The observation location as point in WGS84"))

    location_accuracy = models.CharField(
        max_length=300,
        default="online-map",
        verbose_name=_("Location accuracy"),
        choices=LOCATION_ACCURACY_CHOICES,
        help_text=_("The accuracy of the supplied location."), )

    who = models.ForeignKey(
        User,
        verbose_name=_("Observed by"),
        help_text=_("The observer has to be a registered system user"))

    as_html = models.TextField(
        verbose_name=_("HTML representation"),
        blank=True, null=True, editable=False,
        help_text=_("The cached HTML representation for display purposes."),)

    class Meta:
        """Class options."""

        ordering = ["when", "where"]
        verbose_name = "Encounter"
        verbose_name_plural = "Encounters"
        get_latest_by = "when"

    def __str__(self):
        """The unicode representation."""
        return "Encounter {0} on {1} by {2}".format(self.pk, self.when, self.who)

    def save(self, *args, **kwargs):
        """Cache the HTML representation in `as_html`."""
        self.as_html = self.make_html()
        super(Encounter, self).save(*args, **kwargs)

    # FSM transitions --------------------------------------------------------#
    def can_proofread(self):
        """Return true if this document can be proofread."""
        return True

    @transition(
        field=status,
        source=STATUS_NEW,
        target=STATUS_PROOFREAD,
        conditions=[can_proofread],
        # permission=lambda instance, user: user in instance.all_permitted,
        custom=dict(
            verbose="Mark as proofread",
            explanation=("This record is a faithful representation of the "
                         "data sheet."),
            notify=True,)
        )
    def proofread(self):
        """Mark encounter as proof-read.

        Proofreading compares the attached data sheet with entered values.
        Proofread data is deemed a faithful representation of original data
        captured on a paper field data collection form, or stored in a legacy
        system.
        """
        return

    def can_require_proofreading(self):
        """Return true if this document can be proofread."""
        return True

    @transition(
        field=status,
        source=STATUS_PROOFREAD,
        target=STATUS_NEW,
        conditions=[can_require_proofreading],
        # permission=lambda instance, user: user in instance.all_permitted,
        custom=dict(
            verbose="Require proofreading",
            explanation=("This record deviates from the data source and "
                         "requires proofreading."),
            notify=True,)
        )
    def require_proofreading(self):
        """Mark encounter as having typos, requiring more proofreading.

        Proofreading compares the attached data sheet with entered values.
        If a discrepancy to the data sheet is found, proofreading is required.
        """
        return

    def can_curate(self):
        """Return true if this document can be marked as curated."""
        return True

    @transition(
        field=status,
        source=STATUS_PROOFREAD,
        target=STATUS_CURATED,
        conditions=[can_curate],
        # permission=lambda instance, user: user in instance.all_permitted,
        custom=dict(
            verbose="Mark as trustworthy",
            explanation=("This record is deemed trustworthy."),
            notify=True,)
        )
    def curate(self):
        """Mark encounter as curated.

        Curated data is deemed trustworthy by a subject matter expert.
        """
        return

    def can_revoke_curated(self):
        """Return true if curated status can be revoked."""
        return True

    @transition(
        field=status,
        source=STATUS_CURATED,
        target=STATUS_PROOFREAD,
        conditions=[can_revoke_curated],
        # permission=lambda instance, user: user in instance.all_permitted,
        custom=dict(
            verbose="Flag",
            explanation=("This record cannot be true. This record requires"
                         " review by a subject matter expert."),
            notify=True,)
        )
    def flag(self):
        """Flag as requiring changes to data.

        Curated data is deemed trustworthy by a subject matter expert.
        Revoking curation flags data for requiring changes by an expert.
        """
        return

    def can_publish(self):
        """Return true if this document can be published."""
        return True

    @transition(
        field=status,
        source=STATUS_CURATED,
        target=STATUS_PUBLISHED,
        conditions=[can_publish],
        # permission=lambda instance, user: user in instance.all_permitted,
        custom=dict(
            verbose="Publish",
            explanation=("This record is fit for release."),
            notify=True,)
        )
    def publish(self):
        """Mark encounter as ready to be published.

        Published data has been deemed fit for release by the data owner.
        """
        return

    def can_embargo(self):
        """Return true if encounter can be embargoed."""
        return True

    @transition(
        field=status,
        source=STATUS_PUBLISHED,
        target=STATUS_CURATED,
        conditions=[can_embargo],
        # permission=lambda instance, user: user in instance.all_permitted,
        custom=dict(
            verbose="Embargo",
            explanation=("This record is not fit for release."),
            notify=True,)
        )
    def embargo(self):
        """Mark encounter as NOT ready to be published.

        Published data has been deemed fit for release by the data owner.
        Embargoed data is marked as curated, but not ready for release.
        """
        return

    # HTML display -----------------------------------------------------------#
    @property
    def wkt(self):
        """Return the point coordinates as Well Known Text (WKT)."""
        return self.where.wkt

    @property
    def status_html(self):
        """An HTML div indicating the QA status."""
        tpl = '<div class="popup"><span class="tag tag-{0}">{1}</span></div>'
        return tpl.format(Encounter.STATUS_LABELS[self.status],
                          self.get_status_display())

    @property
    def absolute_admin_url(self):
        """Return the absolute admin change URL."""
        return reverse('admin:{0}_{1}_change'.format(
            self._meta.app_label, self._meta.model_name), args=[self.pk])

    @property
    def admin_url_html(self):
        """An HTML div with a link to the admin change_view."""
        tpl = ('<div class="popup">&nbsp;<a href={0} target="_">'
               '<i class="fa fa-pencil"></i></a></div>')
        return tpl.format(self.absolute_admin_url)

    @property
    def observer_html(self):
        """An HTML string of metadata."""
        tpl = '<div class="popup"><i class="fa fa-{0}"></i>&nbsp;{1}</div>'
        return mark_safe(
            tpl.format("calendar", self.when.strftime('%d/%m/%Y %H:%M:%S %Z')) +
            tpl.format("user", self.who.name))

    @property
    def observation_html(self):
        """An HTML string of Observations."""
        return "".join([o.as_html for o in self.observation_set.all()])

    def make_html(self):
        """Create an HTML representation."""
        tpl = '<h4>Encounter</h4>{0}{1}{2}{3}'
        return mark_safe(tpl.format(self.observer_html, self.observation_html,
                                    self.admin_url_html, self.status_html))


@python_2_unicode_compatible
class AnimalEncounter(Encounter):
    """The encounter of an animal of a species in a certain state of health
    and behaviour.
    """

    TAXON_CHOICES = (
        ("Cheloniidae", "Marine turtles"),
        ("Cetacea", "Whales and Dolphins"),
        ("Pinnipedia", "Pinnipeds"),
        ("Sirenia", "Dugongs"),
        ("Elasmobranchii", "Sharks and Rays"),
        ("na", "Unknown"), )

    TURTLE_SPECIES_CHOICES = (
        ("na", "not observed"),
        # turtles
        ('Natator depressus', 'Natator depressus (Flatback turtle)'),
        ('Chelonia mydas', 'Chelonia mydas (Green turtle)'),
        ('Eretmochelys imbricata', 'Eretmochelys imbricata (Hawksbill turtle)'),
        ('Caretta caretta', 'Caretta caretta (Loggerhead turtle)'),
        ('Lepidochelys olivacea', 'Lepidochelys olivacea (Olive ridley turtle)'),
        ('Dermochelys coriacea', 'Leatherback turtle (Dermochelys coriacea)'),
        ('Chelonia mydas agassazzi', 'Chelonia mydas agassazzi (Black turtle or East Pacific Green)'),
        ('Corolla corolla', 'Corolla corolla (Hatchback turtle)'),
        ('unidentified-turtle', 'Unidentified turtle'),
        # Caretta caretta x Chelonia mydas (Hybrid turtle)
        # Chelonia mydas agassazzi (Black turtle or East Pacific Green)
        # Chelonia mydas x Eretmochelys imbricata (Hybrid turtle)
        # Natator depressus x Caretta caretta (Hybrid turtle)
        # Natator depressus x Chelonia mydas (Hybrid turtle)
        # dolphins
        )
    CETACEAN_SPECIES_CHOICES = (
        ("Delphinus delphis", "Delphinus delphis (Short-beaked common dolphin)"),
        ("Grampus griseus", "Grampus griseus (Risso's dolphin)"),
        ("Lagenodelphis hosei", "Lagenodelphis hosei (Fraser's dolphin)"),
        ("Lagenorhynchus obscurus", "Lagenorhynchus obscurus (Dusky dolphin)"),
        ("Orcaella heinsohni", "Orcaella heinsohni (Australian snubfin dolphin)"),
        ("Sousa sahulensis", "Sousa sahulensis (Australian humpback dolphin)"),
        ("Stenella attenuata", "Stenella attenuata (Pantropical spotted dolphin)"),
        ("Stenella coeruleoalba", "Stenella coeruleoalba (Striped dolphin)"),
        ("Stenella longirostris", "Stenella longirostris (Spinner dolphin)"),
        ("Stenella sp.", "Stenella sp. (Unidentified spotted dolphin)"),
        ("Steno bredanensis", "Steno bredanensis (Rough-toothed dolphin)"),
        ("Tursiops aduncus", "Tursiops aduncus (Indo-Pacific bottlenose dolphin)"),
        ("Tursiops truncatus", "Tursiops truncatus (Offshore bottlenose dolphin)"),
        ("Tursiops sp.", "Tursiops sp. (Unidentified bottlenose dolphin)"),
        ("unidentified-dolphin", "Unidentified dolphin"),
        # whales
        ("Balaenoptera acutorostrata", "Balaenoptera acutorostrata (Dwarf minke whale)"),
        ("Balaenoptera bonaerensis", "Balaenoptera bonaerensis (Antarctic minke whale)<"),
        ("Balaenoptera borealis", "Balaenoptera borealis (Sei whale)"),
        ("Balaenoptera edeni", "Balaenoptera edeni (Bryde's whale)"),
        ("Balaenoptera musculus", "Balaenoptera musculus (Blue whale)"),
        ("Balaenoptera musculus brevicauda", "Balaenoptera musculus brevicauda (Pygmy blue whale)"),
        ("Balaenoptera physalus", "Balaenoptera physalus (Fin whale)"),
        ("Balaenoptera sp.", "Balaenoptera sp. (Unidentified Balaenoptera)"),
        ("Eubalaena australis", "Eubalaena australis (Southern right whale)"),
        ("Feresa attenuata", "Feresa attenuata (Pygmy killer whale)"),
        ("Globicephala macrorhynchus", "Globicephala macrorhynchus (Short-finned pilot whale)"),
        ("Globicephala melas", "Globicephala melas (Long-finned pilot whale)"),
        ("Globicephala sp.", "Globicephala sp. (Unidentified pilot whale)"),
        ("Indopacetus pacificus", "Indopacetus pacificus (Longman's beaked whale)"),
        ("Kogia breviceps", "Kogia breviceps (Pygmy sperm whale)"),
        ("Kogia sima", "Kogia sima (Dwarf sperm whale)"),
        ("Kogia sp.", "Kogia sp. (Unidentified small sperm whale)"),
        ("Megaptera novaeangliae", "Megaptera novaeangliae (Humpback whale)"),
        ("Mesoplodon densirostris", "Mesoplodon densirostris (Blainville's beaked whale)"),
        ("Mesoplodon layardii", "Mesoplodon layardii (Strap-toothed whale)"),
        ("Mesoplodon sp.", "Mesoplodon sp. (Beaked whale)"),
        ("Orcinus orca", "Orcinus orca (Killer whale)"),
        ("Peponocephala electra", "Peponocephala electra (Melon-headed whale)"),
        ("Physeter macrocephalus", "Physeter macrocephalus (Sperm whale)"),
        ("Pseudorca crassidens", "Pseudorca crassidens (False killer whale)"),
        ("Ziphius cavirostris", "Ziphius cavirostris (Cuvier's beaked whale)"),
        ("unidentified-whale", "Unidentified whale"), )

    SPECIES_CHOICES = TURTLE_SPECIES_CHOICES + CETACEAN_SPECIES_CHOICES

    SEX_CHOICES = (
        ("na", "not observed"),
        ("male", "male"),
        ("female", "female"),
        ("na", "sex not determined or not examined"),
        ("intersex", "hermaphrodite or intersex"), )

    MATURITY_CHOICES = (
        ("na", "not observed"),
        # turtle
        ("turtle-hatchling", "hatchling turtle"),
        ("turtle-post-hatchling", "post-hatchling turtle"),
        ("turtle-juvenile", "juvenile turtle"),
        ("turtle-pre-pubsecent-immature", "pre-pubsecent immature turtle"),
        ("turtle-pubsecent-immature", "pubsecent immature turtle"),
        ("turtle-adult-measured", "adult turtle (status determined from carapace and tail measurements)"),
        ("turtle-adult", "adult turtle"),
        ("turtle-unknown", "unknown maturity turtle"),
        # mammal
        ("mammal-unweaned", "unweaned immature mammal"),
        ("mammal-weaned", "weaned immature mammal"),
        ("mammal-adult", "adult mammal"),
        ("mammal-unknown", "unknown maturity mammal"), )

    HEALTH_CHOICES = (
        ("na", "not observed"),
        ('alive', 'Alive (healthy)'),
        ('alive-injured', 'Alive (injured)'),
        ('alive-then-died', 'Initally alive (but died)'),
        ('dead-edible', 'Dead (carcass edible)'),
        ('dead-organs-intact', 'Dead (decomposed but organs intact)'),
        ('dead-advanced', 'Dead (advanced decomposition)'),
        ('dead-mummified', 'Mummified (dead, skin holding bones)'),
        ('dead-disarticulated', 'Disarticulated (dead, no soft tissue remaining)'),
        ('other', 'Other'), )

    # StrandNet: same as above
    # some health status options are confused with management actions (
    # disposal, rehab, euth), cause of death
    #
    # <option value="16">DA - Rescued after disorientation inland by artificial lighting</option>
    # <option value="22">DK - Killed for research</option>
    # <option value="1">DL - Alive and left to natural processes. Not rescued</option>
    # <option value="23">DU - Live but subsequently euthanased</option>
    # <option value="2">DZ - Alive and rescued</option></select>

    ACTIVITY_CHOICES = (
        ("na", "not observed"),
        # nesting:
        ("arriving", "arriving on beach"),
        ("digging-body-pit", "digging body pit"),
        ("excavating-egg-chamber", "excavating egg chamber"),
        ("laying-eggs", "laying eggs"),
        ("filling-in-egg-chamber", "filling in egg chamber"),
        ("returning-to-water", "returning to water"),
        # stranding:
        ("floating", "Floating (dead, sick, unable to dive, drifting in water)"),
        ("beach-washed", "Beach washed (dead, sick or stranded on beach/coast)"),
        ("beach-jumped", "Beach jumped"),
        ("carcass-tagged-released", "Carcass tagged and released"),
        ("carcass-inland", "Carcass or butchered remains found removed from coast"),
        ("captivity", "In captivity"),
        ("non-breeding", "General non-breeding activity (swimming, sleeping, feeding, etc.)"),
        ("other", "other activity"), )

    # primary activity
    # <option value="20">? - Unspecified</option>
    # <option value="1">B - B - to be determined)</option>
    # <option value="2">B? - B? - to be determined)</option>
    # <option value="3">BE - BE - to be determined</option>
    # <option value="4">BF - Floating (dead, sick, unable to dive, drifting in water)</option>
    # <option value="5">BJ - Beach Jumped</option>
    # <option value="7">BR - Carcass or butchered remains found removed from coast</option>
    # <option value="6">BW - Beach washed (dead, sick or stranded on beach/coast)</option>
    # <option value="8">C - Courting</option>
    # <option value="21">CT - Carcass tagged and released to test stranding recovery and water currents.</option>
    # <option value="9">J - In captivity</option>
    # <option value="10">N - Nesting and internesting</option>
    # <option value="11">P - Predated (killed)</option>
    # <option value="12">PC - Predated by crocodile (killed)</option>
    # <option value="13">PD - Predated by dog or dingo (killed)</option>
    # <option value="14">PF - Predated by fish (killed)</option>
    # <option value="15">PR - Predated by raptor (killed)</option>
    # <option value="16">PS - Predated by shark (killed)</option>
    # <option value="17">R - Released</option>
    # <option value="18">S - General non-breeding activity (swimming, sleeping, feeding, ...)</option>
    # <option value="19">Z - Tag found not attached to animal</option></select>
    # # secondary activity
    # <option value="30">? - ? - to be determined</option>
    # <option value="2">BJ - Non-Nesting: Beach jumped</option>
    # <option value="3">BW - Non-Nesting: Beach washed</option>
    # <option value="75">CT - Carcass tagged and released to test stranding recovery and water currents.</option>
    # <option value="31">F? - F? - to be determined</option>
    # <option value="10">FC - Fisheries: Fishing - captured in arrowhead fish trap</option>
    # <option value="11">FD - Fisheries: Sucked/picked up by dredge</option>
    # <option value="36">FG - Fisheries: Captured with gaff from boat</option>
    # <option value="35">FI - Fisheries: Crabbing - trapped inside a crab pot</option>
    # <option value="12">FL - Fisheries: Fishing - hooked by fishing line; included SCP shark-hooks</option>
    # <option value="13">FN - Fisheries: Fishing - captured by netting</option>
    # <option value="14">FP - Fisheries: Tangled in float-line to crab-pot, anchor line, trace to shark-hook, etc</option>
    # <option value="15">FS - Fisheries: Fishing - speared, or captured by a diver attaching a line to the animal</option>
    # <option value="16">FT - Fisheries: Fishing - trawling</option>
    # <option value="17">FZ - Fisheries: Trapped in ghost-net</option>
    # <option value="32">L - L - to be determined</option>
    # <option value="56">NJ - Non-Nesting: Rodeo - night time</option>
    # <option value="55">NS - Non-Nesting: SCUBA/snorkelling - night time</option>
    # <option value="6">P - Non-Nesting: Observed but not captured</option>
    # <option value="57">PA - Non-Nesting: Observation from aerial survey</option>
    # <option value="58">PI - Non-Nesting: Image recorded during underwater video monitoring</option>
    # <option value="4">RJ - Non-Nesting: Rodeo - day time</option>
    # <option value="5">S - Non-Nesting: SCUBA/snorkelling - day time</option>
    # <option value="33">T - T - to be determined</option>
    # <option value="20">TA - Trapped: Trapped by land reclaimation</option>
    # <option value="21">TE - Trapped: Trapped in electricity power plant water intake system</option>
    # <option value="59">TS - Non-Nesting: Located by satellite telemetry</option>
    # <option value="22">TT - Trapped: Trapped in creek at low tide</option>
    # <option value="34">X - X - to be determined</option>
    # <option value="1">X* - Nesting: Laid</option></select>

    HABITAT_CHOICES = (
        ("na", "not observed"),
        ("beach", "B - Beach: Below the vegetation line of the grass slope"),
        ("bays-estuaries", "BE - Bays, estuaries and other enclosed shallow soft sediments"),
        ("dune", "D - Dune"),
        ("dune-constructed-hard-substrate", "DC - Dune: Constructed hard substrate (concrete slabs, timber floors, helipad)"),
        ("dune-grass-area", "DG - Dune: Grass area"),
        ("dune-compacted-path", "DH - Dune: Hard compacted areas (road ways, paths)"),
        ("dune-rubble", "DR - Dune: Rubble, usually coral"),
        ("dune-bare-sand", "DS - Dune: Bare sand area"),
        ("dune-beneath-vegetation", "DT - Dune: Beneath tree or shrub"),
        ("slope-front-dune", "S - Slope: Front slope of dune"),
        ("sand-flats", "SF - Sand flats"),
        ("slope-grass", "SG - Slope: Grass area"),
        ("slope-bare-sand", "SS - Slope: Bare sand area"),
        ("slope-beneath-vegetation", "ST - Slope: Beneath tree or shrub"),
        ("below-mean-spring-high-water-mark", "HW - Below the mean spring high water line or current level of inundation"),
        ("lagoon-patch-reef", "LP - Lagoon: Patch reef"),
        ("lagoon-open-sand", "LS - Lagoon: Open sand areas, typically shallow"),
        ("mangroves", "M - Mangroves"),
        ("reef-coral", "R - Reef: Coral reef"),
        ("reef-crest-front-slope", "RC - Reef: Reef crest (dries at low water) and front reef slope areas"),
        ("reef-flat", "RF - Reef: Reef flat, dries at low tide"),
        ("reef-seagrass-flats", "RG - Coral reef with seagrass flats"),
        ("reef-rocky", "RR - Reef: Rocky reef, e.g. adjacent to mainland"),
        ("open-water", "OW - Open water, including inter reefal areas"), )

    taxon = models.CharField(
        max_length=300,
        verbose_name=_("Taxonomic group"),
        choices=TAXON_CHOICES,
        default="na",
        help_text=_("The taxonomic group of the animal."), )

    species = models.CharField(
        max_length=300,
        verbose_name=_("Species"),
        choices=SPECIES_CHOICES,
        default="unidentified",
        help_text=_("The species of the animal."), )

    sex = models.CharField(
        max_length=300,
        default="na",
        verbose_name=_("Sex"),
        choices=SEX_CHOICES,
        help_text=_("The animal's sex."), )

    maturity = models.CharField(
        max_length=300,
        default="na",
        verbose_name=_("Maturity"),
        choices=MATURITY_CHOICES,
        help_text=_("The animal's maturity."), )

    health = models.CharField(
        max_length=300,
        verbose_name=_("Health status"),
        choices=HEALTH_CHOICES,
        default="na",
        help_text=_("On a scale from the Fresh Prince of Bel Air to 80s Hair "
                    "Metal: how dead and decomposed is the animal?"), )

    activity = models.CharField(
        max_length=300,
        default="na",
        verbose_name=_("Activity"),
        choices=ACTIVITY_CHOICES,
        help_text=_("The animal's activity at the time of observation."), )

    behaviour = models.TextField(
        verbose_name=_("Behaviour"),
        blank=True, null=True,
        help_text=_("Notes on condition or behaviour if alive."), )

    habitat = models.CharField(
        max_length=500,
        verbose_name=_("Habitat"),
        choices=HABITAT_CHOICES,
        default="na",
        help_text=_("The habitat in which the animal was encountered."), )

    class Meta:
        """Class options."""

        ordering = ["when", "where"]
        verbose_name = "Animal Encounter"
        verbose_name_plural = "Animal Encounters"
        get_latest_by = "when"

    def __str__(self):
        """The unicode representation."""
        tpl = "AnimalEncounter {0} on {1} by {2} of {3}, {4} {5} {6} on {7}"
        return tpl.format(
            self.pk,
            self.when.strftime('%d/%m/%Y %H:%M:%S %Z'),
            self.who.name,
            self.get_species_display(),
            self.get_health_display(),
            self.get_maturity_display(),
            self.get_sex_display(),
            self.get_habitat_display())

    def save(self, *args, **kwargs):
        """Cache the HTML representation in `as_html`."""
        self.as_html = self.make_html()
        super(AnimalEncounter, self).save(*args, **kwargs)

    @property
    def is_standing(self):
        """Hacky way of splitting AnimalEncounters into strandings (not alive
        and healthy) and other (tagging) observations.
        """
        return self.health != 'alive'

    @property
    def animal_html(self):
        """An HTML string of Observations."""
        tpl = '<h4>{0}</h4><i class="fa fa-heartbeat"></i>&nbsp;{1} {2} {3} {4}'
        return mark_safe(
            tpl.format(self.get_species_display(), self.get_health_display(),
                       self.get_maturity_display(), self.get_sex_display(),
                       self.get_habitat_display()))

    def make_html(self):
        """Create an HTML representation."""
        tpl = "{0}{1}{2}{3}{4}"
        return mark_safe(tpl.format(self.animal_html, self.observer_html,
                                    self.observation_html, self.admin_url_html,
                                    self.status_html))


# @python_2_unicode_compatible
# class TurtleEncounter(AnimalEncounter):
#     """The encounter of a turtle in a certain state of health and activity.
#
#     TurtleEncounters include nesting/tagging and stranding encounters.
#     TurtleEncounters limit species choices to turtle species and maturity
#     choices to turtle-specific options.
#     """
#
#     class Meta:
#         """Class options."""
#
#         ordering = ["when", "where"]
#         verbose_name = "Turtle Encounter"
#         verbose_name_plural = "Turtle Encounters"
#         get_latest_by = "when"
#
#     def __str__(self):
#         """The unicode representation."""
#         tpl = "Turtle Encounter {0} on {1} by {2} of {3}, {4} {5} {6} on {7}"
#         return tpl.format(
#             self.pk,
#             self.when.strftime('%d/%m/%Y %H:%M:%S %Z'),
#             self.who.name,
#             self.get_species_display(),
#             self.get_health_display(),
#             self.get_maturity_display(),
#             self.get_sex_display(),
#             self.get_habitat_display())
#
#     def save(self, *args, **kwargs):
#         """Cache the HTML representation in `as_html`."""
#         self.as_html = self.make_html()
#         super(TurtleEncounter, self).save(*args, **kwargs)
#
#
# @python_2_unicode_compatible
# class CetaceanEncounter(AnimalEncounter):
#     """The encounter of a cetacean in a certain state of health and activity.
#
#     CetaceanEncounters currently support strandings.
#     Species choices are limited to dolphins and whales; maturity choices are
#     limited to cetacean-specific options.
#     """
#
#     class Meta:
#         """Class options."""
#
#         ordering = ["when", "where"]
#         verbose_name = "Cetacean Encounter"
#         verbose_name_plural = "Cetacean Encounters"
#         get_latest_by = "when"
#
#     def __str__(self):
#         """The unicode representation."""
#         tpl = "Cetacean Encounter {0} on {1} by {2} of {3}, {4} {5} {6} on {7}"
#         return tpl.format(
#             self.pk,
#             self.when.strftime('%d/%m/%Y %H:%M:%S %Z'),
#             self.who.name,
#             self.get_species_display(),
#             self.get_health_display(),
#             self.get_maturity_display(),
#             self.get_sex_display(),
#             self.get_habitat_display())
#
#     def save(self, *args, **kwargs):
#         """Cache the HTML representation in `as_html`."""
#         self.as_html = self.make_html()
#         super(CetaceanEncounter, self).save(*args, **kwargs)


@python_2_unicode_compatible
class TurtleNestEncounter(Encounter):
    """The encounter of turtle nest during its life cycle.

    Stages:

    * false crawl (aborted nesting attempt)
    * new (turtle is present, observed during nesting/tagging)
    * fresh (morning after, observed during trach count)
    * predated (nest and eggs destroyed by predator)
    * hatched (eggs hatched)
    """

    NEST_AGE_CHOICES = (
        ("false-crawl", "false crawl"),
        ("nesting-turtle-present", "new nest, turtle present"),
        ("fresh", "new nest, turtle absent"),
        ("predated", "nest and eggs destroyed by predator"),
        ("hatched", "hatched nest"), )

    nest_age = models.CharField(
        max_length=300,
        default="new",
        verbose_name=_("Nest age"),
        choices=NEST_AGE_CHOICES,
        help_text=_("The nest age and type."), )

    species = models.CharField(
        max_length=300,
        verbose_name=_("Species"),
        choices=AnimalEncounter.SPECIES_CHOICES,
        default="unidentified",
        help_text=_("The species of the animal."), )

    habitat = models.CharField(
        max_length=500,
        verbose_name=_("Habitat"),
        choices=AnimalEncounter.HABITAT_CHOICES,
        default="na",
        help_text=_("The habitat in which the nest was encountered."), )

    class Meta:
        """Class options."""

        ordering = ["when", "where"]
        verbose_name = "Turtle Nest Encounter"
        verbose_name_plural = "Turtle Nest Encounters"
        get_latest_by = "when"

    def __str__(self):
        """The unicode representation."""
        return "{0} nest in {1}, {2}".format(
            self.get_species_display(),
            self.get_habitat_display(),
            self.get_nest_age_display(), )

    @property
    def nest_html(self):
        tpl = '<div class="popup">{0}</div>'
        return mark_safe(tpl.format(self.__str__()))

    def make_html(self):
        """Create an HTML representation."""
        tpl = '<h4>{0}</h4>{1}{2}{3}{4}'
        return mark_safe(tpl.format(
            self.nest_html,
            self.observer_html,
            self.observation_html,
            self.admin_url_html,
            self.status_html, ))

    def save(self, *args, **kwargs):
        """Cache the HTML representation in `as_html`."""
        self.as_html = self.make_html()
        super(TurtleNestEncounter, self).save(*args, **kwargs)


# Observation models ---------------------------------------------------------#
@python_2_unicode_compatible
class Observation(PolymorphicModel, models.Model):
    """The Observation base class for encounter observations."""

    encounter = models.ForeignKey(
        Encounter,
        blank=True, null=True,
        verbose_name=_("Encounter"),
        help_text=("The Encounter during which the observation was made"),)

    def __str__(self):
        """The unicode representation."""
        return "Obs {0} for {1}".format(self.pk, self.encounter.__str__())

    @property
    def as_html(self):
        """An HTML representation."""
        return mark_safe('<div class="popup">{0}</div>'.format(self.__str__()))

    @property
    def observation_name(self):
        """Model name."""
        return self.polymorphic_ctype.model


@python_2_unicode_compatible
class MediaAttachment(Observation):
    """A media attachment to an Encounter."""

    MEDIA_TYPE_CHOICES = (
        ('data_sheet', 'Original data sheet'),
        ('photograph', 'Photograph'),
        ('other', 'Other'),)

    media_type = models.CharField(
        max_length=300,
        verbose_name=_("Attachment type"),
        choices=MEDIA_TYPE_CHOICES,
        default="other",
        help_text=_("What is the attached file about?"),)

    title = models.CharField(
        max_length=300,
        verbose_name=_("Attachment name"),
        blank=True, null=True,
        help_text=_("Give the attachment a representative name"),)

    attachment = models.FileField(
        upload_to='attachments/%Y/%m/%d/',
        verbose_name=_("File attachment"),
        help_text=_("Upload the file"),)

    def __str__(self):
        """The unicode representation."""
        return "Media {0} {1} for {2}".format(
            self.pk, self.title, self.encounter.__str__())

    @property
    def as_html(self):
        """An HTML representation."""
        tpl = ('<div class="popup"><i class="fa fa-film"></i>'
               '&nbsp;<a href="{0}" target="_">{1}</a></div>')
        return mark_safe(tpl.format(self.attachment.url, self.title))


@python_2_unicode_compatible
class TagObservation(Observation):
    """An Observation of an identifying tag on an observed entity.

    The identifying tag can be a flipper tag on a turtle, a PIT tag,
    a satellite tag, a barcode on a sample taken off an animal, a whisker ID
    from a picture of a pinniped, a genetic fingerprint or similar.

    The tag has its own life cycle through stages of production, delivery,
    affiliation with an animal, repeated sightings and disposal.

    The life cycle stages will vary between tag types.

    A TagObservation will find the tag in exactly one of the life cycle stages.

    The life history of each tag can be reconstructed from the sum of all of its
    TagObservations.

    As TagObservations can sometimes occur without an Observation of an animal, the
    FK to Observations is optional.
    """

    TYPE_CHOICES = (
        ('flipper-tag', 'Flipper Tag'),
        ('pit-tag', 'PIT Tag'),
        ('satellite-tag', 'Satellite Tag'),
        ('physical-sample', 'Physical Sample'),
        ('biopsy-sample', 'Biopsy Sample'),
        ('genetic-fingerprint', 'Genetic Fingerprint (DNA sample)'),
        ('whisker-id', 'Whisker ID'),
        ('other', 'Other'),)

    STATUS_CHOICES = (
        ('ordered', 'ordered from manufacturer'),
        ('produced', 'produced by manufacturer'),
        ('delivered', 'delivered to HQ'),
        ('allocated', 'allocated to field team'),
        ('attached', 'attached new to an animal'),
        ('recaptured', 're-sighted as attached to animal'),
        ('detached', 'taken off an animal'),
        ('found', 'found detached'),
        ('returned', 'returned to HQ'),
        ('decommissioned', 'decommissioned from active tag pool'),
        ('destroyed', 'destroyed'),
        ('observed', 'observed in any other context, see comments'), )

    SIDE_CHOICES = (
        ("L", "left front flipper"),
        ("R", "right front flipper"),
        ("C", "carapace"),
        ("N", "neck"),
        ("O", "other, see comments"), )

    POSITION_CHOICES = (
        ("1", "1st scale from body/head"),
        ("2", "2nd scale from body/head"),
        ("3", "3rd scale from body/head"),
        ("O", "other, see comments"), )

    tag_type = models.CharField(
        max_length=300,
        verbose_name=_("Tag type"),
        choices=TYPE_CHOICES,
        default="flipper-tag",
        help_text=_("What kind of tag is it?"),)

    side = models.CharField(
        max_length=300,
        verbose_name=_("Tag side"),
        choices=SIDE_CHOICES,
        default="L",
        help_text=_("Is the tag on the left or right front flipper?"),)

    position = models.CharField(
        max_length=300,
        verbose_name=_("Tag position"),
        choices=POSITION_CHOICES,
        default="1",
        help_text=_("Counting from inside, to which flipper scale is the "
                    "tag attached?"),)

    name = models.CharField(
        max_length=1000,
        verbose_name=_("Tag ID"),
        help_text=_("The ID of a tag must be unique within the tag type."),)

    status = models.CharField(
        max_length=300,
        verbose_name=_("Tag status"),
        choices=STATUS_CHOICES,
        default="recaptured",
        help_text=_("The status this tag was seen in, or brought into."),)

    comments = models.TextField(
        verbose_name=_("Comments"),
        blank=True, null=True,
        help_text=_("Any other comments or notes."),)

    def __str__(self):
        """The unicode representation."""
        return "{0} {1} {2} on {3}, {4}".format(
            self.get_tag_type_display(),
            self.name, self.get_status_display(),
            self.get_side_display(), self.get_position_display())

    @property
    def history_url(self):
        """The list view of all observations of this tag."""
        cl = reverse("admin:observations_tagobservation_changelist")
        return "{0}?q={1}".format(cl, urllib.quote_plus(self.name))

    @property
    def as_html(self):
        """An HTML representation."""
        tpl = ('<div class="popup"><i class="fa fa-tag"></i>&nbsp;{0}&nbsp;'
               '<a href={1} target="_" class="btn btn-sm">'
               '<i class="fa fa-history"></i></a></div>')
        return mark_safe(tpl.format(self.__str__(), self.history_url))


@python_2_unicode_compatible
class DistinguishingFeatureObservation(Observation):
    """DistinguishingFeature observation."""

    OBSERVATION_CHOICES = (
        ("na", "Not observed"),
        ("absent", "Confirmed absent"),
        ("present", "Confirmed present"),)

    OBSERVATION_ICONS = {
        "na": "fa fa-question-circle-o",
        "absent": "fa fa-times",
        "present": "fa fa-check"}

    PHOTO_CHOICES = (
        ("na", "Not applicable"),
        ("see photos", "See attached photos for details"),)

    PHOTO_ICONS = {
        "na": "fa fa-question-circle-o",
        "see photos": "fa fa-check"}

    damage_injury = models.CharField(
        max_length=300,
        verbose_name=_("Obvious damage or injuries"),
        choices=OBSERVATION_CHOICES,
        default="na",
        help_text=_(""),)

    scanned_for_pit_tags = models.CharField(
        max_length=300,
        verbose_name=_("Scanned for PIT tags"),
        choices=OBSERVATION_CHOICES,
        default="na",
        help_text=_(""),)

    missing_limbs = models.CharField(
        max_length=300,
        verbose_name=_("Missing limbs"),
        choices=OBSERVATION_CHOICES,
        default="na",
        help_text=_(""),)

    barnacles = models.CharField(
        max_length=300,
        verbose_name=_("Barnacles"),
        choices=OBSERVATION_CHOICES,
        default="na",
        help_text=_(""),)

    algal_growth = models.CharField(
        max_length=300,
        verbose_name=_("Algal growth on carapace"),
        choices=OBSERVATION_CHOICES,
        default="na",
        help_text=_(""),)

    tagging_scars = models.CharField(
        max_length=300,
        verbose_name=_("Tagging scars"),
        choices=OBSERVATION_CHOICES,
        default="na",
        help_text=_(""),)

    propeller_damage = models.CharField(
        max_length=300,
        verbose_name=_("Propeller strike damage"),
        choices=OBSERVATION_CHOICES,
        default="na",
        help_text=_(""),)

    entanglement = models.CharField(
        max_length=300,
        verbose_name=_("Entanglement"),
        choices=OBSERVATION_CHOICES,
        default="na",
        help_text=_("Entanglement in anthropogenic debris"),)

    see_photo = models.CharField(
        max_length=300,
        verbose_name=_("See attached photos"),
        choices=PHOTO_CHOICES,
        default="na",
        help_text=_("More relevant detail in attached photos"),)

    comments = models.TextField(
        verbose_name=_("Comments"),
        blank=True, null=True,
        help_text=_("Further comments on distinguising features."),)

    def __str__(self):
        """The unicode representation."""
        return "Distinguishing Features {0} of {1}".format(
            self.pk, self.encounter.__str__())

    @property
    def as_html(self):
        """An HTML representation."""
        tpl = ('<div class="popup"><i class="fa fa-eye"></i>&nbsp;{0}'
               '&nbsp<i class="{1}"></i></div>')
        return mark_safe(
            tpl.format("Damage", self.OBSERVATION_ICONS[self.damage_injury]) +
            tpl.format("PIT tags scanned", self.OBSERVATION_ICONS[self.scanned_for_pit_tags]) +
            tpl.format("Missing Limbs", self.OBSERVATION_ICONS[self.missing_limbs]) +
            tpl.format("Barnacles", self.OBSERVATION_ICONS[self.barnacles]) +
            tpl.format("Algal growth", self.OBSERVATION_ICONS[self.algal_growth]) +
            tpl.format("Tagging scars", self.OBSERVATION_ICONS[self.tagging_scars]) +
            tpl.format("Propeller damage", self.OBSERVATION_ICONS[self.propeller_damage]) +
            tpl.format("Entanglement", self.OBSERVATION_ICONS[self.entanglement]) +
            tpl.format("More in photos", self.PHOTO_ICONS[self.see_photo]))


@python_2_unicode_compatible
class ManagementAction(Observation):
    """
    Management actions following an AnimalEncounter.

    E.g, disposal, rehab, euthanasia.
    """

    management_actions = models.TextField(
        verbose_name=_("Management Actions"),
        blank=True, null=True,
        help_text=_("Managment actions taken. Keep updating as appropriate."),)

    comments = models.TextField(
        verbose_name=_("Comments"),
        blank=True, null=True,
        help_text=_("Any other comments or notes."),)

    def __str__(self):
        """The unicode representation."""
        return "Management Action {0} of {1}".format(
            self.pk, self.encounter.__str__())

    @property
    def as_html(self):
        """An HTML representation."""
        tpl = '<div class="popup"><i class="fa fa-arrrow-right"></i>&nbsp;{0}</div>'
        return mark_safe(tpl.format(self.management_actions))


@python_2_unicode_compatible
class TurtleMorphometricObservation(Observation):
    """Morphometric measurements of a turtle."""

    ACCURACY_CHOICES = (
        ("unknown", "Unknown"),
        ("estimated", "Estimated"),
        ("measured", "Measured"),)

    ACCURACY_ICONS = {
        "unknown": "fa fa-question-circle-o",
        "estimated": "fa fa-comment-o",
        "measured": "fa fa-balance-scale"}

    curved_carapace_length_mm = models.PositiveIntegerField(
        verbose_name=_("Curved Carapace Length (mm)"),
        blank=True, null=True,
        help_text=_("The Curved Carapace Length in millimetres."),)

    curved_carapace_length_accuracy = models.CharField(
        max_length=300,
        default="unknown",
        verbose_name=_("Curved Carapace Length Accuracy"),
        choices=ACCURACY_CHOICES,
        help_text=_("The measurement type as indication of accuracy."),)

    curved_carapace_notch_mm = models.PositiveIntegerField(
        verbose_name=_("Curved Carapace Notch (mm)"),
        blank=True, null=True,
        help_text=_("The Curved Carapace Notch in millimetres."),)

    curved_carapace_notch_accuracy = models.CharField(
        max_length=300,
        default="unknown",
        verbose_name=_("Curved Carapace Notch Accuracy"),
        choices=ACCURACY_CHOICES,
        help_text=_("The measurement type as indication of accuracy."),)

    curved_carapace_width_mm = models.PositiveIntegerField(
        verbose_name=_("Curved Carapace Width (mm)"),
        blank=True, null=True,
        help_text=_("Curved Carapace Width in millimetres."),)

    curved_carapace_width_accuracy = models.CharField(
        max_length=300,
        default="unknown",
        verbose_name=_("Curved Carapace Width Accuracy"),
        choices=ACCURACY_CHOICES,
        help_text=_("The measurement type as indication of accuracy."),)

    tail_length_mm = models.PositiveIntegerField(
        verbose_name=_("Tail Length (mm)"),
        blank=True, null=True,
        help_text=_("The Tail Length, measured from carapace in millimetres."),)

    tail_length_accuracy = models.CharField(
        max_length=300,
        default="unknown",
        verbose_name=_("Tail Length Accuracy"),
        choices=ACCURACY_CHOICES,
        help_text=_("The measurement type as indication of accuracy."),)

    maximum_head_width_mm = models.PositiveIntegerField(
        verbose_name=_("Maximum Head Width (mm)"),
        blank=True, null=True,
        help_text=_("The Maximum Head Width in millimetres."),)

    maximum_head_width_accuracy = models.CharField(
        max_length=300,
        default="unknown",
        verbose_name=_("Maximum Head Width Accuracy"),
        choices=ACCURACY_CHOICES,
        help_text=_("The measurement type as indication of accuracy."),)

    def __str__(self):
        """The unicode representation."""
        return "Turtle Morphometrics {0} for {1}".format(
            self.pk, self.encounter)

    @property
    def as_html(self):
        """An HTML representation."""
        tpl = ('<div class="popup"><i class="fa fa-bar-chart"></i>&nbsp;{0}'
               '&nbsp;{1}&nbsp;mm&nbsp;<i class="{2}"></i></div>')
        return mark_safe(
            tpl.format("CCL", self.curved_carapace_length_mm,
                       self.ACCURACY_ICONS[self.curved_carapace_length_accuracy]) +
            tpl.format("CCN", self.curved_carapace_notch_mm,
                       self.ACCURACY_ICONS[self.curved_carapace_notch_accuracy]) +
            tpl.format("CCW", self.curved_carapace_width_mm,
                       self.ACCURACY_ICONS[self.curved_carapace_width_accuracy]) +
            tpl.format("TL", self.tail_length_mm,
                       self.ACCURACY_ICONS[self.tail_length_accuracy]) +
            tpl.format("HW", self.maximum_head_width_mm,
                       self.ACCURACY_ICONS[self.maximum_head_width_accuracy])
            )


@python_2_unicode_compatible
class TurtleNestObservation(Observation):
    """Turtle nest observations."""

    BEACH_POSITION_CHOICES = (
        ("below-hwm", "below high water mark"),
        ("above-hw", "above high water mark, below dune"),
        ("dune-edge", "edge of dune, beginning of spinifex"),
        ("in-dune", "inside dune, spinifex"), )

    nest_position = models.CharField(
        max_length=300,
        default="unknown",
        verbose_name=_("Beach position"),
        choices=BEACH_POSITION_CHOICES,
        help_text=_("The position of the nest on the beach."), )

    eggs_laid = models.BooleanField(
        verbose_name=_("Did the turtle lay eggs?"),
        default=False,
        help_text=_("Did round, white objects leave the turtle's butt?"), )

    egg_count = models.PositiveIntegerField(
        verbose_name=_("Total number of eggs laid"),
        blank=True, null=True,
        help_text=_("The total number of eggs laid."), )

    # add:
    # nest_depth_top, nest_depth_bottom,
    # nest contents (9)
    # temperature (sand, air, water, egg)

    def __str__(self):
        """The unicode representation."""
        return "Nest {0} with {1} eggs".format(
            self.get_nest_position_display(),
            self.egg_count)

    @property
    def as_html(self):
        """An HTML representation."""
        tpl = ('<div class="popup"><i class="fa fa-home"></i>&nbsp;{0}</div>')
        return mark_safe(tpl.format(self.__str__()))


@python_2_unicode_compatible
class TurtleDamageObservation(Observation):
    """Observation of turtle damages or injuries."""

    BODY_PART_CHOICES = (
        ("head", "head"),
        ("plastron", "plastron"),
        ("carapace", "carapace"),
        ("tail", "tail"),
        ("flipper-front-left", "front left flipper"),
        ("flipper-front-right", "front right flipper"),
        ("flipper-rear-left", "rear left flipper"),
        ("flipper-rear-right", "rear right flipper"),
        ("whole-turtle", "whole turtle"), )

    DAMAGE_TYPE_CHOICES = (
        ("minor-trauma", "minor trauma"),
        ("major-trauma", "major trauma"),
        ("tip-amputated", "tip amputation"),
        ("amputated-from-nail", "amputation from nail"),
        ("amputated-half", "half amputation"),
        ("amputated-entirely", "entire amputation"),
        ("cuts", "cuts"),
        ("deformity", "deformity"),
        ("propeller-strike", "propeller strike"),
        ("entanglement", "entanglement"),
        ("other", "other"), )

    DAMAGE_AGE_CHOICES = (
        ("healed-entirely", "entirely healed"),
        ("healed-partially", "partially healed"),
        ("fresh", "fresh"), )

    body_part = models.CharField(
        max_length=300,
        default="whole-turtle",
        verbose_name=_("Affected body part"),
        choices=BODY_PART_CHOICES,
        help_text=_("The body part affected by the observed damage."), )

    damage_type = models.CharField(
        max_length=300,
        default="minor-trauma",
        verbose_name=_("Damage age"),
        choices=DAMAGE_TYPE_CHOICES,
        help_text=_("The type of the damage."), )

    damage_age = models.CharField(
        max_length=300,
        default="healed-entirely",
        verbose_name=_("Damage age"),
        choices=DAMAGE_AGE_CHOICES,
        help_text=_("The age of the damage."), )

    description = models.TextField(
        verbose_name=_("Description"),
        blank=True, null=True,
        help_text=_("A description of the damage."), )

    def __str__(self):
        """The unicode representation."""
        return "{0}: {1} {2}".format(
            self.get_body_part_display(),
            self.get_damage_age_display(),
            self.get_damage_type_display(), )

    @property
    def as_html(self):
        """An HTML representation."""
        tpl = ('<div class="popup"><i class="fa fa-bolt"></i>&nbsp;{0}</div>')
        return mark_safe(tpl.format(self.__str__()))

# TODO  add TrackTallyObservation, CecaceanMorphometricObservation
