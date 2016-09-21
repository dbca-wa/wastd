# -*- coding: utf-8 -*-
"""Observation models.

These models support opportunistic encounters with stranded, dead, injured,
nesting turtles and possibly other wildlife, such as cetaceans and pinnipeds.

Species use a local name list, but should lookup a webservice.
This Observation is generic for all species. Other Models can FK this Model
to add species-specific measurements.

Observer name / address / phone / email is captured through the observer being
a system user.

The combination of species and health determines subsequent measurements and
actions:

* [turtle, dugong, cetacean] damage observation
* [turtle, dugong, cetacean] distinguishing features
* [taxon] morphometrics
* [flipper, pit, sat] tag observation
* disposal actions

"""
from __future__ import unicode_literals, absolute_import

import itertools
import urllib
import slugify

# from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.gis.db import models as geo_models
from django.core.urlresolvers import reverse
from django.template import Context, loader
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from polymorphic.models import PolymorphicModel
from django_fsm import FSMField, transition
from django_fsm_log.decorators import fsm_log_by

from wastd.users.models import User

# Lookups --------------------------------------------------------------------#

BODY_PART_DEFAULT = "whole"
TURTLE_BODY_PART_CHOICES = (
    ("head", "head"),
    ("eyes", "eyes"),
    ("neck", "neck"),
    ("plastron", "plastron"),
    ("carapace", "carapace"),
    ("internals", "internals"),
    ("cloaca", "cloaca"),
    ("tail", "tail"),
    ("flipper-front-left-1", "front left flipper, 1st scale from body"),
    ("flipper-front-left-2", "front left flipper, 2nd scale from body"),
    ("flipper-front-left-3", "front left flipper, 3rd scale from body"),
    ("flipper-front-left", "front left flipper"),
    ("flipper-front-right-1", "front right flipper, 1st scale from body"),
    ("flipper-front-right-2", "front right flipper, 2nd scale from body"),
    ("flipper-front-right-3", "front right flipper, 3rd scale from body"),
    ("flipper-front-right", "front right flipper"),
    ("flipper-rear-left", "rear left flipper"),
    ("flipper-rear-right", "rear right flipper"),
    ("shoulder-left", "left shoulder"),
    ("shoulder-right", "right shoulder"),
    (BODY_PART_DEFAULT, "whole turtle"),
    ('other', 'Other'), )

TAG_TYPE_DEFAULT = 'flipper-tag'
TAG_TYPE_CHOICES = (
    (TAG_TYPE_DEFAULT, 'Flipper Tag'),
    ('pit-tag', 'PIT Tag'),
    ('satellite-tag', 'Satellite Tag'),
    ('data-logger', 'Data Logger'),
    ('blood-sample', 'Blood Sample'),
    ('biopsy-sample', 'Biopsy Sample'),
    ('stomach-content-sample', 'Stomach Content Sample'),
    ('physical-sample', 'Physical Sample'),
    ('egg-sample', 'Egg Sample'),
    ('temperature-logger', 'Temperature Logger'),
    ('other', 'Other'),)

TAG_STATUS_DEFAULT = 'resighted'
TAG_STATUS_APPLIED_NEW = 'applied-new'
TAG_STATUS_CHOICES = (                                        # TRT_TAG_STATES
    ('ordered', 'ordered from manufacturer'),
    ('produced', 'produced by manufacturer'),
    ('delivered', 'delivered to HQ'),
    ('allocated', 'allocated to field team'),
    (TAG_STATUS_APPLIED_NEW, 'applied new'),        # A1, AE
    (TAG_STATUS_DEFAULT, 're-sighted associated with animal'),  # OX, P, P_OK, RQ, P_ED
    ('reclinched', 're-sighted and reclinced on animal'),  # RC
    ('removed', 'taken off animal'),                      # OO, R
    ('found', 'found detached'),
    ('returned', 'returned to HQ'),
    ('decommissioned', 'decommissioned'),
    ('destroyed', 'destroyed'),
    ('observed', 'observed in any other context, see comments'), )

TAG_STATUS_RESIGHTED = ('resighted', 'reclinched', 'removed')
TAG_STATUS_ON_ANIMAL = (TAG_STATUS_APPLIED_NEW, TAG_STATUS_RESIGHTED)

NA_VALUE = "na"
NA = ((NA_VALUE, "not observed"), )

TAXON_CHOICES_DEFAULT = "Cheloniidae"
TAXON_CHOICES = NA + (
    (TAXON_CHOICES_DEFAULT, "Marine turtles"),
    ("Cetacea", "Whales and Dolphins"),
    ("Pinnipedia", "Pinnipeds"),
    ("Sirenia", "Dugongs"),
    ("Elasmobranchii", "Sharks and Rays"), )

TURTLE_SPECIES_CHOICES = (
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
    # dolphins
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

SPECIES_CHOICES = NA + TURTLE_SPECIES_CHOICES + CETACEAN_SPECIES_CHOICES

SEX_CHOICES = (
    (NA_VALUE, "unknown sex"),
    ("male", "male"),
    ("female", "female"),
    ("intersex", "hermaphrodite or intersex"), )

TURTLE_MATURITY_CHOICES = (
    ("hatchling", "hatchling"),
    ("post-hatchling", "post-hatchling"),
    ("juvenile", "juvenile"),
    ("pre-pubsecent-immature", "pre-pubsecent immature"),
    ("pubsecent-immature", "pubsecent immature"),
    ("adult-measured", "adult (status determined from carapace and tail measurements)"), )

MAMMAL_MATURITY_CHOICES = (
    ("unweaned", "unweaned immature"),
    ("weaned", "weaned immature"), )

MATURITY_CHOICES = TURTLE_MATURITY_CHOICES + MAMMAL_MATURITY_CHOICES +\
    (("adult", "adult"),
     ("unknown", "unknown maturity"), )

HEALTH_CHOICES = (
    (NA_VALUE, "unknown health"),
    ('alive', 'alive, healthy'),
    ('alive-injured', 'alive, injured'),
    ('alive-then-died', 'alive, then died'),
    ('dead-edible', 'dead, fresh'),
    ('dead-organs-intact', 'dead, organs intact'),
    ('dead-advanced', 'dead, organs decomposed'),
    ('dead-mummified', 'dead, mummified'),
    ('dead-disarticulated', 'dead, disarticulated'),
    ('other', 'other'), )

# StrandNet: same as above
# some health status options are confused with management actions
# (disposal, rehab, euth), cause of death
#
# <option value="16">DA - Rescued after disorientation inland by artificial lighting</option>
# <option value="22">DK - Killed for research</option>
# <option value="1">DL - Alive and left to natural processes. Not rescued</option>
# <option value="23">DU - Live but subsequently euthanased</option>
# <option value="2">DZ - Alive and rescued</option></select>

NESTING_ACTIVITY_CHOICES = (
    ("arriving", "arriving on beach"),
    ("digging-body-pit", "digging body pit"),
    ("excavating-egg-chamber", "excavating egg chamber"),
    ("laying-eggs", "laying eggs"),
    ("filling-in-egg-chamber", "filling in egg chamber"),
    ("returning-to-water", "returning to water"), )

STRANDING_ACTIVITY_CHOICES = (
    ("floating", "floating (dead, sick, unable to dive, drifting in water)"),
    ("beach-washed", "beach washed (dead, sick or stranded on beach/coast)"),
    ("beach-jumped", "beach jumped"),
    ("carcass-tagged-released", "carcass tagged and released"),
    ("carcass-inland", "carcass or butchered remains found removed from coast"),
    ("captivity", "in captivity"),
    ("non-breeding", "general non-breeding activity (swimming, sleeping, feeding, etc.)"),
    ("other", "other activity"), )

ACTIVITY_CHOICES = NA + NESTING_ACTIVITY_CHOICES + STRANDING_ACTIVITY_CHOICES
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

BEACH_POSITION_CHOICES = (
    ("beach-below-high-water", _("below high water mark")),
    ("beach-above-high-water", _("above high water mark, below dune")),
    ("beach-edge-of-vegetation", _("edge of dune and vegetation")),
    ("in-dune-vegetation", _("inside dune and vegetation")), )

HABITAT_CHOICES = NA + BEACH_POSITION_CHOICES + (
    ("beach", "beach (below vegetation line)"),
    ("bays-estuaries", "bays, estuaries and other enclosed shallow soft sediments"),
    ("dune", "dune"),
    ("dune-constructed-hard-substrate", "dune, constructed hard substrate (concrete slabs, timber floors, helipad)"),
    ("dune-grass-area", "dune, grass area"),
    ("dune-compacted-path", "dune, hard compacted areas (road ways, paths)"),
    ("dune-rubble", "dune, rubble, usually coral"),
    ("dune-bare-sand", "dune, bare sand area"),
    ("dune-beneath-vegetation", "dune, beneath tree or shrub"),
    ("slope-front-dune", "dune, front slope"),
    ("sand-flats", "sand flats"),
    ("slope-grass", "slope, grass area"),
    ("slope-bare-sand", "slope, bare sand area"),
    ("slope-beneath-vegetation", "slope, beneath tree or shrub"),
    ("below-mean-spring-high-water-mark", "below the mean spring high water line or current level of inundation"),
    ("lagoon-patch-reef", "lagoon, patch reef"),
    ("lagoon-open-sand", "lagoon, open sand areas"),
    ("mangroves", "mangroves"),
    ("reef-coral", "coral reef"),
    ("reef-crest-front-slope", "reef crest (dries at low water) and front reef slope areas"),
    ("reef-flat", "reef flat, dries at low tide"),
    ("reef-seagrass-flats", "coral reef with seagrass flats"),
    ("reef-rocky", "rocky reef"),
    ("open-water", "open water"), )

HABITAT_WATER = ("lagoon-patch-reef", "lagoon-open-sand", "mangroves",
                 "reef-coral", "reef-crest-front-slope", "reef-flat",
                 "reef-seagrass-flats", "reef-rocky", "open-water")

NEST_AGE_CHOICES = (
    ("false-crawl", "False crawl"),
    ("nesting-turtle-present", "New nest (turtle present)"),
    ("fresh", "New nest (turtle absent)"),
    ("predated", "Predated nest"),
    ("hatched", "Hatched nest"), )

OBSERVATION_CHOICES = (
    (NA_VALUE, "NA"),
    ("absent", "Confirmed absent"),
    ("present", "Confirmed present"),)

OBSERVATION_ICONS = {
    NA_VALUE: "fa fa-question-circle-o",
    "absent": "fa fa-times",
    "present": "fa fa-check"}

PHOTO_CHOICES = NA + (("see photos", "See attached photos for details"),)

PHOTO_ICONS = {
    NA_VALUE: "fa fa-question-circle-o",
    "see photos": "fa fa-check"}

ACCURACY_CHOICES = (
    ("unknown", "Unknown"),
    ("estimated", "Estimated"),
    ("measured", "Measured"),)

ACCURACY_ICONS = {
    NA_VALUE: "fa fw fa-question-circle-o",
    "unknown": "fa fw fa-question-circle-o",
    "estimated": "fa fw fa-comment-o",
    "measured": "fa fw fa-balance-scale"}

DAMAGE_TYPE_CHOICES = (
    # Amputations
    ("tip-amputated", "tip amputation"),
    ("amputated-from-nail", "amputation from nail"),
    ("amputated-half", "half amputation"),
    ("amputated-entirely", "entire amputation"),

    # Epiphytes and gross things
    ("barnacles", "barnacles"),
    ("algal-growth", "algal growth"),
    ("tumor", "tumor"),

    # Tags
    ("tag-scar", "tag scar"),
    ("tag-seen", "tag seen but not identified"),

    # Injuries
    ("cuts", "cuts"),
    ("boat-strike", "boat or propeller strike"),
    ("entanglement", "entanglement"),

    # Morphologic aberrations
    ("deformity", "deformity"),

    # Catch-all
    ("other", "other"), )

DAMAGE_AGE_CHOICES = (
    ("healed-entirely", "entirely healed"),
    ("healed-partially", "partially healed"),
    ("fresh", "fresh"), )


# End lookups ----------------------------------------------------------------#
#
#
# Encounter models -----------------------------------------------------------#
@python_2_unicode_compatible
class Encounter(PolymorphicModel, geo_models.Model):
    """The base Encounter class.

    * When: Datetime of encounter, stored in UTC, entered and displayed in local
      timezome.
    * Where: Point in WGS84.
    * Who: The observer has to be a registered system user.
    * Source: The previous point of truth for the record.
    * Source ID: The ID of the encounter at the previous point of truth. This
      can be a corporate file number, a database primary key, and likely is
      prefixed or post-fixed. Batch imports can (if they use the ID consistently)
      use the ID to identify previously imported records and avoid duplication.

    A suggested naming standard for paper records is
    ``<prefix><date><running-number>``, with possible

    * prefix indicates data type (stranding, tagging, nest obs etc)
    * date is reversed Y-m-d
    * a running number caters for multiple records of the same prefix and date

    These Paper record IDs should be recorded on the original paper forms
    (before scanning), used as file names for the PDF'd scans, and typed into
    WAStD.

    The QA status can only be changed through transition methods, not directly.
    Changes to the QA status, as wells as versions of the data are logged to
    preserve the data lineage.
    """

    STATUS_NEW = 'new'
    STATUS_PROOFREAD = 'proofread'
    STATUS_CURATED = 'curated'
    STATUS_PUBLISHED = 'published'

    STATUS_CHOICES = (
        (STATUS_NEW, _("New")),
        (STATUS_PROOFREAD, _("Proofread")),
        (STATUS_CURATED, _("Curated")),
        (STATUS_PUBLISHED, _("Published")), )

    STATUS_LABELS = {
        STATUS_NEW: "danger",
        STATUS_PROOFREAD: "warning",
        STATUS_CURATED: "info",
        STATUS_PUBLISHED: "success", }

    LOCATION_DEFAULT = "1000"
    LOCATION_ACCURACY_CHOICES = (
        ("10", _("GPS reading at exact location (10 m)")),
        (LOCATION_DEFAULT, _("Site centroid or place name (1 km)")),
        ("10000", _("Rough estimate (10 km)")), )

    SOURCE_DEFAULT = "direct"
    SOURCE_CHOICES = (
        (SOURCE_DEFAULT, _("Direct entry")),
        ("paper", _("Paper data sheet")),
        ("wamtram", _("WAMTRAM 2 tagging DB")),
        ("ntp-exmouth", _("NTP Access DB Exmouth")),
        ("ntp-broome", _("NTP Access DB Broome")),)

    source = models.CharField(
        max_length=300,
        verbose_name=_("Data Source"),
        default=SOURCE_DEFAULT,
        choices=SOURCE_CHOICES,
        help_text=_("Where was this record captured initially?"), )

    source_id = models.CharField(
        max_length=1000,
        blank=True, null=True,
        verbose_name=_("Source ID"),
        help_text=_("The ID of the record in the original source."), )

    status = FSMField(
        default=STATUS_NEW,
        choices=STATUS_CHOICES,
        verbose_name=_("QA Status"))

    when = models.DateTimeField(
        verbose_name=_("Observed on"),
        help_text=_("The observation datetime, shown as local time "
                    "(no daylight savings), stored as UTC."))

    where = geo_models.PointField(
        srid=4326,
        verbose_name=_("Observed at"),
        help_text=_("The observation location as point in WGS84"))

    location_accuracy = models.CharField(
        max_length=300,
        verbose_name=_("Location accuracy (m)"),
        default=LOCATION_DEFAULT,
        choices=LOCATION_ACCURACY_CHOICES,
        help_text=_("The accuracy of the supplied location."), )

    name = models.CharField(
        max_length=1000,
        editable=False,
        blank=True, null=True,
        verbose_name=_("Animal Name"),
        help_text=_("The animal's earliest associated flipper tag ID."),)

    observer = models.ForeignKey(
        User,
        verbose_name=_("Measured by"),
        related_name="observer",
        help_text=_("The person who executes the measurements, "
                    "source of measurement bias"))

    reporter = models.ForeignKey(
        User,
        verbose_name=_("Recorded by"),
        related_name="reporter",
        help_text=_("The person who writes the data sheet in the field, "
                    "source of handwriting and spelling errors"))

    as_html = models.TextField(
        verbose_name=_("HTML representation"),
        blank=True, null=True, editable=False,
        help_text=_("The cached HTML representation for display purposes."),)

    class Meta:
        """Class options."""

        ordering = ["when", "where"]
        unique_together = ("source", "source_id")
        verbose_name = "Encounter"
        verbose_name_plural = "Encounters"
        get_latest_by = "when"

    @property
    def opts(self):
        """Make _meta accessible from templates."""
        return self._meta

    def __str__(self):
        """The unicode representation."""
        return "Encounter {0} on {1} by {2}".format(self.pk, self.when, self.observer)

    @property
    def short_name(self):
        """A short, often unique, human-readable representation of the encounter.

        Slugified and dash-separated:

        * Date of encounter as YYYY-mm-dd
        * longitude in WGS 84 DD, rounded to 4 decimals (<10m),
        * latitude in WGS 84 DD, rounded to 4 decimals (<10m), (missing sign!!)
        * health,
        * maturity,
        * species.

        The short_name could be non-unique for encounters of multiple stranded
        animals of the same species and deadness.
        """
        return slugify.slugify("-".join([
            self.when.strftime("%Y-%m-%d-%H-%M-%S"),
            str(round(self.where.get_x(), 4)).replace(".", "-"),
            str(round(self.where.get_y(), 4)).replace(".", "-"),
            ]))

    def save(self, *args, **kwargs):
        """Cache the HTML representation in `as_html` and set the source ID.

        Source ID will be auto-generated from ``short_name`` but is not
        guaranteed to be unique. The User will be prompted to provide a unique
        source ID if necessary, e.g. by appending a running number.
        """
        self.as_html = self.get_popup()
        if not self.source_id:
            self.source_id = self.short_name
        if not self.name and self.inferred_name:
            self.name = self.inferred_name
        super(Encounter, self).save(*args, **kwargs)

    # HTML popup -------------------------------------------------------------#
    def get_popup(self):
        """Generate HTML popup content."""
        t = loader.get_template("popup/{0}.html".format(self._meta.model_name))
        c = Context({"original": self})
        return mark_safe(t.render(c))

    @property
    def observations(self):
        """Return Observations as list."""
        return self.observation_set.all()

    @property
    def latitude(self):
        """Return the WGS 84 DD latitude."""
        return self.where.get_y()

    @property
    def longitude(self):
        """Return the WGS 84 DD longitude."""
        return self.where.get_x()

    @property
    def crs(self):
        """Return the location CRS."""
        return self.where.srs.name

    @property
    def status_label(self):
        """Return the boostrap tag-* CSS label flavour for the QA status."""
        return Encounter.STATUS_LABELS[self.status]

    @property
    def image_url(self):
        """Return the URL of the first attached photograph or none."""
        try:
            return self.observation_set.instance_of(
                MediaAttachment
                ).filter(
                    mediaattachment__media_type="photograph"
                ).first().attachment.url
        except:
            return None

    @property
    def absolute_admin_url(self):
        """Return the absolute admin change URL."""
        return reverse('admin:{0}_{1}_change'.format(
            self._meta.app_label, self._meta.model_name), args=[self.pk])

    # Name -------------------------------------------------------------------#
    def set_name(self, name):
        """Set the animal name to a given value."""
        self.name = name
        self.save()
        print("{0} name set to {1}".format(self.__str__(), name))

    @property
    def inferred_name(self):
        """Return the inferred name from related new capture if existing."""
        # TODO less dirty
        try:
            return [enc.name for enc in self.related_encounters
                    if enc.is_new_capture][0]
        except:
            return None

    def set_name_in_related_encounters(self, name):
        """Set the animal name in all related AnimalEncounters."""
        [a.set_name(name) for a in self.related_encounters]

    def set_name_and_propagate(self, name):
        """Set the animal name in this and all related Encounters."""
        # self.set_name(name)  # already contained in next line
        self.set_name_in_related_encounters(name)

    @property
    def related_encounters(self):
        """Return all Encounters with the same Animal.

        This algorithm collects all Encounters with the same animal by
        traversing an Encounter's TagObservations and their encounter histories.

        The algorithm starts with the Encounter (``self``) as initial
        known Encounter (``known_enc``), and ``self.tags`` as both initial known
        (``known_tags``) and new TagObs (``new_tags``).
        While there are new TagObs, a "while" loop harvests new encounters:

        * For each tag in ``new_tags``, retrieve the encounter history.
        * Combine and deduplicate the encounter histories
        * Remove known encounters and call this set of encounters ``new_enc``.
        * Add ``new_enc`` to ``known_enc``.
        * Combine and deduplicate all tags of all encounters in ``new_enc`` and
          call this set of TabObservations ``new_tags``.
        * Add ``new_tags`` to ``known_tags``.
        * Repeat the loop if the list of new tags is not empty.

        Finally, deduplicate and return ``known_enc``. These are all encounters
        that concern the same animal as this (self) encounter, as proven through
        the shared presence of TagObservations.
        """
        known_enc = [self, ]
        known_tags = list(self.tags)
        new_enc = []
        new_tags = self.tags
        show_must_go_on = True

        while show_must_go_on:
            new_enc = TagObservation.encounter_histories(
                new_tags, exclude_encounters=known_enc)
            known_enc.extend(new_enc)
            new_tags = Encounter.tag_lists(new_enc)
            known_tags += new_tags
            show_must_go_on = len(new_tags) > 0

        return list(set(known_enc))

    @property
    def tags(self):
        """Return a queryset of TagObservations."""
        return self.observation_set.instance_of(TagObservation)

    @property
    def flipper_tags(self):
        """Return a queryset of Flipper Tag Observations."""
        return self.observation_set.instance_of(TagObservation).filter(
            tagobservation__tag_type='flipper-tag')

    @property
    def primary_flipper_tag(self):
        """Return the TagObservation of the primary flipper tag."""
        return self.flipper_tags.order_by('tagobservation__tag_location').first()

    @classmethod
    def tag_lists(cls, encounter_list):
        """Return the related tags of list of encounters.

        TODO double-check performance
        """
        return list(set(itertools.chain.from_iterable(
            [e.tags for e in encounter_list])))

    @property
    def is_new_capture(self):
        """Return whether the Encounter is a new capture (hint: never).

        Encounters can involve tags, but are never new captures.
        AnimalEncounters override this property, as they can be new captures.
        """
        return False

    # FSM transitions --------------------------------------------------------#
    def can_proofread(self):
        """Return true if this document can be proofread."""
        return True

    @fsm_log_by
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
    def proofread(self, by=None):
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

    @fsm_log_by
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
    def require_proofreading(self, by=None):
        """Mark encounter as having typos, requiring more proofreading.

        Proofreading compares the attached data sheet with entered values.
        If a discrepancy to the data sheet is found, proofreading is required.
        """
        return

    def can_curate(self):
        """Return true if this document can be marked as curated."""
        return True

    @fsm_log_by
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
    def curate(self, by=None):
        """Mark encounter as curated.

        Curated data is deemed trustworthy by a subject matter expert.
        """
        return

    def can_revoke_curated(self):
        """Return true if curated status can be revoked."""
        return True

    @fsm_log_by
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
    def flag(self, by=None):
        """Flag as requiring changes to data.

        Curated data is deemed trustworthy by a subject matter expert.
        Revoking curation flags data for requiring changes by an expert.
        """
        return

    def can_publish(self):
        """Return true if this document can be published."""
        return True

    @fsm_log_by
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
    def publish(self, by=None):
        """Mark encounter as ready to be published.

        Published data has been deemed fit for release by the data owner.
        """
        return

    def can_embargo(self):
        """Return true if encounter can be embargoed."""
        return True

    @fsm_log_by
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
    def embargo(self, by=None):
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


@python_2_unicode_compatible
class AnimalEncounter(Encounter):
    """The encounter of an animal of a species.

    Extends the base Encounter class with:

    * taxonomic group (choices), can be used to filter remaining form choices
    * species (choices)
    * sex (choices)
    * maturity (choices)
    * health (choices)
    * activity (choices)
    * behaviour (free text)
    * habitat (choices)
    """

    taxon = models.CharField(
        max_length=300,
        verbose_name=_("Taxonomic group"),
        choices=TAXON_CHOICES,
        default=TAXON_CHOICES_DEFAULT,
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

    checked_for_injuries = models.CharField(
        max_length=300,
        verbose_name=_("Checked for injuries"),
        choices=OBSERVATION_CHOICES,
        default="na",
        help_text=_(""),)

    scanned_for_pit_tags = models.CharField(
        max_length=300,
        verbose_name=_("Scanned for PIT tags"),
        choices=OBSERVATION_CHOICES,
        default="na",
        help_text=_(""),)

    checked_for_flipper_tags = models.CharField(
        max_length=300,
        verbose_name=_("Checked for flipper tags"),
        choices=OBSERVATION_CHOICES,
        default="na",
        help_text=_(""),)

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
            self.observer.name,
            self.get_species_display(),
            self.get_health_display(),
            self.get_maturity_display(),
            self.get_sex_display(),
            self.get_habitat_display())

    def save(self, *args, **kwargs):
        """Cache the HTML representation in `as_html`."""
        self.as_html = self.get_popup()
        super(AnimalEncounter, self).save(*args, **kwargs)

    @property
    def short_name(self):
        """A short, often unique, human-readable representation of the encounter.

        Slugified and dash-separated:

        * Date of encounter as YYYY-mm-dd
        * longitude in WGS 84 DD, rounded to 4 decimals (<10m),
        * latitude in WGS 84 DD, rounded to 4 decimals (<10m), (missing sign!!)
        * health,
        * maturity,
        * species,
        * name if available (requires "update names" and tag obs)

        The short_name could be non-unique for encounters of multiple stranded
        animals of the same species and deadness.
        """
        nameparts = [
            self.when.strftime("%Y-%m-%d-%H-%M-%S"),
            str(round(self.where.get_x(), 4)).replace(".", "-"),
            str(round(self.where.get_y(), 4)).replace(".", "-"),
            self.health,
            self.maturity,
            self.sex,
            self.species,
            ]
        if self.name is not None:
            nameparts.append(self.name)
        return slugify.slugify("-".join(nameparts))

    @property
    def is_stranding(self):
        """Return whether the Encounters is stranding or tagging.

        If the animal is not "alive", it's a stranding encounter, else it's a
        tagging encounter.
        """
        return self.health != 'alive'

    @property
    def is_new_capture(self):
        """Return whether this Encounter is a new capture.

        New captures are named after their primary flipper tag.
        An Encounter is a new capture if there are:

        * no associated TagObservations of ``is_recapture`` status
        * at least one associated TabObservation of ``is_new`` status
        """
        new_tagobs = set([x for x in self.flipper_tags if x.is_new])
        old_tagobs = set([x for x in self.flipper_tags if x.is_recapture])
        has_new_tagobs = len(new_tagobs) > 0
        has_old_tagobs = len(old_tagobs) > 0
        return (has_new_tagobs and not has_old_tagobs)


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

    nest_age = models.CharField(
        max_length=300,
        default="new",
        verbose_name=_("Nest age"),
        choices=NEST_AGE_CHOICES,
        help_text=_("The nest age and type."), )

    species = models.CharField(
        max_length=300,
        verbose_name=_("Species"),
        choices=SPECIES_CHOICES,
        default="na",
        help_text=_("The species of the animal."), )

    habitat = models.CharField(
        max_length=500,
        verbose_name=_("Habitat"),
        choices=HABITAT_CHOICES,
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
        return "{0} of {1} in {2}".format(
            self.get_nest_age_display(),
            self.get_species_display(),
            self.get_habitat_display(), )

    def save(self, *args, **kwargs):
        """Cache the HTML representation in `as_html`."""
        self.as_html = self.get_popup()
        super(TurtleNestEncounter, self).save(*args, **kwargs)


# Observation models ---------------------------------------------------------#
@python_2_unicode_compatible
class Observation(PolymorphicModel, models.Model):
    """The Observation base class for encounter observations.

    Everything happens somewhere, at a time, to someone, and someone records it.
    Therefore, an Observation must happen during an Encounter.
    """

    encounter = models.ForeignKey(
        Encounter,
        verbose_name=_("Encounter"),
        help_text=("The Encounter during which the observation was made"),)

    def __str__(self):
        """The unicode representation."""
        return "Obs {0} for {1}".format(self.pk, self.encounter.__str__())

    @property
    def as_html(self):
        """An HTML representation."""
        t = loader.get_template("popup/{0}.html".format(self._meta.model_name))
        c = Context({"original": self})
        return mark_safe(t.render(c))

    @property
    def observation_name(self):
        """The concrete model name.

        This method will inherit down the polymorphic chain, and always return
        the actual child model's name.

        `observation_name` can be included as field e.g. in API serializers,
        so e.g. a writeable serializer would know which child model to `create`
        or `update`.
        """
        return self.polymorphic_ctype.model

    @property
    def latitude(self):
        """The encounter's latitude."""
        return self.encounter.where.get_y() or ''

    @property
    def longitude(self):
        """The encounter's longitude."""
        return self.encounter.where.get_x() or ''

    def datetime(self):
        """The encounter's timestamp."""
        return self.encounter.when or ''


def encounter_media(instance, filename):
    """Return an upload file path for an encounter media attachment."""
    if not instance.encounter.id:
        instance.encounter.save()
    return 'encounter/{0}/{1}'.format(instance.encounter.source_id, filename)


@python_2_unicode_compatible
class MediaAttachment(Observation):
    """A media attachment to an Encounter."""

    MEDIA_TYPE_CHOICES = (
        ('data_sheet', _('Data sheet')),
        ('communication', _('Communication record')),
        ('photograph', _('Photograph')),
        ('other', _('Other')), )

    media_type = models.CharField(
        max_length=300,
        verbose_name=_("Attachment type"),
        choices=MEDIA_TYPE_CHOICES,
        default="photograph",
        help_text=_("What is the attached file about?"),)

    title = models.CharField(
        max_length=300,
        verbose_name=_("Attachment name"),
        blank=True, null=True,
        help_text=_("Give the attachment a representative name"),)

    attachment = models.FileField(
        upload_to=encounter_media,
        max_length=500,
        verbose_name=_("File attachment"),
        help_text=_("Upload the file"),)

    def __str__(self):
        """The unicode representation."""
        return "Media {0} {1} for {2}".format(
            self.pk, self.title, self.encounter.__str__())


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

    Flipper Tag Status as per WAMTRAM:

    * # = tag attached new, number NA, need to double-check number
    * P, p: re-sighted as attached to animal, no actions taken or necessary
    * do not use: 0L, A2, M, M1, N
    * AE = A1
    * P_ED = near flipper edge, might fall off soon
    * PX = tag re-sighted, but operator could not read tag ID (e.g. turtle running off)
    * RQ = tag re-sighted, tag was "insecure", but no action was recorded

    Recaptured tags: Need to record state (open, closed, tip locked or not)
    as feedback to taggers to improve their tagging technique.

    PIT tag status:

    * applied and did read OK
    * applied and did not read (but still inside and might read later on)

    Sample status:

    * taken off animal
    * handed to lab
    * done science to it
    * handed in report

    Animal Name:
    All TagObservations of one animal are linked by shared encounters or
    shared tag names. The earliest associated flipper tag name is used as the
    animal's name, and transferred onto all related TagObservations.
    """

    tag_type = models.CharField(
        max_length=300,
        verbose_name=_("Tag type"),
        choices=TAG_TYPE_CHOICES,
        default="flipper-tag",
        help_text=_("What kind of tag is it?"),)

    tag_location = models.CharField(
        max_length=300,
        verbose_name=_("Tag position"),
        choices=TURTLE_BODY_PART_CHOICES,
        default=BODY_PART_DEFAULT,
        help_text=_("Where is the tag attached, or the sample taken from?"),)

    name = models.CharField(
        max_length=1000,
        verbose_name=_("Tag ID"),
        help_text=_("The ID of a tag must be unique within the tag type."),)

    status = models.CharField(
        max_length=300,
        verbose_name=_("Tag status"),
        choices=TAG_STATUS_CHOICES,
        default=TAG_STATUS_DEFAULT,
        help_text=_("The status this tag was seen in, or brought into."),)

    handler = models.ForeignKey(
        User,
        blank=True, null=True,
        verbose_name=_("Handled by"),
        related_name="tag_handler",
        help_text=_("The person in physical contact with the tag or sample"))

    recorder = models.ForeignKey(
        User,
        blank=True, null=True,
        verbose_name=_("Recorded by"),
        related_name="tag_recorder",
        help_text=_("The person who records the tag observation"))

    comments = models.TextField(
        verbose_name=_("Comments"),
        blank=True, null=True,
        help_text=_("Any other comments or notes."),)

    def __str__(self):
        """The unicode representation."""
        return "{0} {1} {2} on {3}".format(
            self.get_tag_type_display(),
            self.name,
            self.get_status_display(),
            self.get_tag_location_display())

    @classmethod
    def encounter_history(cls, tagname):
        """Return the related encounters of all TagObservations of a given tag name."""
        return list(set([t.encounter for t in cls.objects.filter(name=tagname)]))

    @classmethod
    def encounter_histories(cls, tagname_list, exclude_encounters=[]):
        """Return the related encounters of all tag names.

        TODO double-check performance
        """
        return [encounter for encounter in list(set(itertools.chain.from_iterable(
            [TagObservation.encounter_history(t.name) for t in tagname_list])))
                if encounter not in exclude_encounters]

    @property
    def is_new(self):
        """Return wheter the TagObservation is the first association with the animal."""
        return self.status == TAG_STATUS_APPLIED_NEW

    @property
    def is_recapture(self):
        """Return whether the TabObservation is a recapture."""
        return self.status in TAG_STATUS_RESIGHTED

    @property
    def history_url(self):
        """The list view of all observations of this tag."""
        cl = reverse("admin:observations_tagobservation_changelist")
        return "{0}?q={1}".format(cl, urllib.quote_plus(self.name))


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


@python_2_unicode_compatible
class TurtleMorphometricObservation(Observation):
    """Morphometric measurements of a turtle."""

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
        verbose_name=_("Curved Carapace Length to notch (mm)"),
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

    handler = models.ForeignKey(
        User,
        blank=True, null=True,
        verbose_name=_("Handled by"),
        related_name="morphometric_handler",
        help_text=_("The person conducting the measurements"))

    recorder = models.ForeignKey(
        User,
        blank=True, null=True,
        verbose_name=_("Recorded by"),
        related_name="morphometric_recorder",
        help_text=_("The person recording the measurements"))

    def __str__(self):
        """The unicode representation."""
        return "Turtle Morphometrics {0} for {1}".format(
            self.pk, self.encounter)


@python_2_unicode_compatible
class TurtleNestObservation(Observation):
    """Turtle nest observations.

    This model supports data sheets for:

    * Turtle nest observation during tagging
    * Turtle nest excavation a few days after hatching

    """

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

    no_egg_shells = models.PositiveIntegerField(
        verbose_name=_("Egg shells"),
        blank=True, null=True,
        help_text=_("The number of egg shells in the nest."), )

    no_live_hatchlings = models.PositiveIntegerField(
        verbose_name=_("Live hatchlings"),
        blank=True, null=True,
        help_text=_("The number of in the nest."),)

    no_dead_hatchlings = models.PositiveIntegerField(
        verbose_name=_("Dead hatchlings"),
        blank=True, null=True,
        help_text=_("The number of dead hatchlings in the nest."),)

    no_undeveloped_eggs = models.PositiveIntegerField(
        verbose_name=_("Undeveloped eggs"),
        blank=True, null=True,
        help_text=_("The number of undeveloped eggs in the nest."),)

    no_dead_embryos = models.PositiveIntegerField(
        verbose_name=_("Dead embryos"),
        blank=True, null=True,
        help_text=_("The number of dead embryos in the nest."),)

    no_dead_full_term_embryos = models.PositiveIntegerField(
        verbose_name=_("Dead full term embryos"),
        blank=True, null=True,
        help_text=_("The number of dead full term embryos in the nest."),)

    no_depredated_eggs = models.PositiveIntegerField(
        verbose_name=_("Depredated eggs`"),
        blank=True, null=True,
        help_text=_("The number of depredated eggs in the nest."),)

    no_unfertilized = models.PositiveIntegerField(
        verbose_name=_("Unfertilized eggs"),
        blank=True, null=True,
        help_text=_("The number of unfertilized eggs in the nest."),)

    no_yolkless_eggs = models.PositiveIntegerField(
        verbose_name=_("Yolkless eggs"),
        blank=True, null=True,
        help_text=_("The number of yolkless eggs in the nest."),)

    nest_depth_top = models.PositiveIntegerField(
        verbose_name=_("Nest depth (top) mm"),
        blank=True, null=True,
        help_text=_("The depth of sand above the eggs in mm."),)

    nest_depth_bottom = models.PositiveIntegerField(
        verbose_name=_("Nest depth (bottom) mm"),
        blank=True, null=True,
        help_text=_("The depth of the lowest eggs in mm."),)

    sand_temp = models.FloatField(
        verbose_name=_("Sand temperature"),
        blank=True, null=True,
        help_text=_("The sand temperature in degree Celsius."),)

    air_temp = models.FloatField(
        verbose_name=_("Air temperature"),
        blank=True, null=True,
        help_text=_("The air temperature in degree Celsius."),)

    water_temp = models.FloatField(
        verbose_name=_("Water temperature"),
        blank=True, null=True,
        help_text=_("The water temperature in degree Celsius."),)

    egg_temp = models.FloatField(
        verbose_name=_("Egg temperature"),
        blank=True, null=True,
        help_text=_("The egg temperature in degree Celsius."),)

    def __str__(self):
        """The unicode representation."""
        return "Nest {0} with {1} eggs".format(
            self.get_nest_position_display(),
            self.egg_count)


@python_2_unicode_compatible
class TurtleDamageObservation(Observation):
    """Observation of turtle damages or injuries."""

    body_part = models.CharField(
        max_length=300,
        default="whole-turtle",
        verbose_name=_("Affected body part"),
        choices=TURTLE_BODY_PART_CHOICES,
        help_text=_("The body part affected by the observed damage."), )

    damage_type = models.CharField(
        max_length=300,
        default="minor-trauma",
        verbose_name=_("Damage type"),
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


@python_2_unicode_compatible
class TrackTallyObservation(Observation):
    """Observation of turtle track tallies and signs of predation."""

    false_crawls_caretta_caretta = models.PositiveIntegerField(
        verbose_name=_("False Crawls Loggerhead"),
        blank=True, null=True,
        help_text=_("The tally of false crawls of Caretta caretta (Loggerhead turtle)."),)

    false_crawls_chelonia_mydas = models.PositiveIntegerField(
        verbose_name=_("False Crawls Green"),
        blank=True, null=True,
        help_text=_("The tally of false crawls of "
                    "Chelonia mydas (Green turtle)."),)

    false_crawls_eretmochelys_imbricata = models.PositiveIntegerField(
        verbose_name=_("False Crawls Hawksbill"),
        blank=True, null=True,
        help_text=_("The tally of false crawls of "
                    "Eretmochelys imbricata (Hawksbill turtle)."),)

    false_crawls_natator_depressus = models.PositiveIntegerField(
        verbose_name=_("False Crawls Flatback"),
        blank=True, null=True,
        help_text=_("The tally of false crawls of "
                    "Natator depressus (Flatback turtle)."),)

    false_crawls_lepidochelys_olivacea = models.PositiveIntegerField(
        verbose_name=_("False Crawls Olive ridley"),
        blank=True, null=True,
        help_text=_("The tally of false crawls of "
                    "Lepidochelys olivacea (Olive ridley turtle)."),)

    false_crawls_na = models.PositiveIntegerField(
        verbose_name=_("False Crawls of unknown species"),
        blank=True, null=True,
        help_text=_("The tally of false crawls of unknown species."),)

    fox_predation = models.CharField(
        max_length=300,
        verbose_name=_("Fox predation"),
        choices=OBSERVATION_CHOICES,
        default="na",
        help_text=_(""),)

    dog_predation = models.CharField(
        max_length=300,
        verbose_name=_("Dog predation"),
        choices=OBSERVATION_CHOICES,
        default="na",
        help_text=_(""),)

    dingo_predation = models.CharField(
        max_length=300,
        verbose_name=_("Dingo predation"),
        choices=OBSERVATION_CHOICES,
        default="na",
        help_text=_(""),)

    croc_predation = models.CharField(
        max_length=300,
        verbose_name=_("Crocodile predation"),
        choices=OBSERVATION_CHOICES,
        default="na",
        help_text=_(""),)

    goanna_predation = models.CharField(
        max_length=300,
        verbose_name=_("Goanna predation"),
        choices=OBSERVATION_CHOICES,
        default="na",
        help_text=_(""),)

    bird_predation = models.CharField(
        max_length=300,
        verbose_name=_("Bird predation"),
        choices=OBSERVATION_CHOICES,
        default="na",
        help_text=_(""),)

    def __str__(self):
        """The unicode representation."""
        t1 = ('TrackTally: {0} LH, {1} GN, {2} HB, {3} FB, {4} NA')
        return t1.format(
            self.false_crawls_caretta_caretta,
            self.false_crawls_chelonia_mydas,
            self.false_crawls_eretmochelys_imbricata,
            self.false_crawls_natator_depressus,
            self.false_crawls_na,
            )

# TODO add CecaceanMorphometricObservation for cetacean strandings
