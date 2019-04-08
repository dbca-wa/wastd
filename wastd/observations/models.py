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
from __future__ import absolute_import, unicode_literals

import itertools
import logging
import urllib
from datetime import timedelta

import slugify
from dateutil import tz
from django.contrib.gis.db import models as geo_models
# from django.core.urlresolvers import reverse
from django.db import models
# from durationfield.db.models.fields.duration import DurationField
from django.db.models.fields import DurationField
from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
from django.template import loader
# from django.contrib.gis.db.models.query import GeoQuerySet
from django.urls import reverse
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django_fsm import FSMField, transition
from django_fsm_log.decorators import fsm_log_by
from django_fsm_log.models import StateLog
from polymorphic.models import PolymorphicModel
from rest_framework.reverse import reverse as rest_reverse
from shared.utils import sanitize_tag_label

from wastd.users.models import User

logger = logging.getLogger(__name__)

# Lookups --------------------------------------------------------------------#

SOURCE_DEFAULT = "direct"
SOURCE_CHOICES = (
    (SOURCE_DEFAULT, _("Direct entry")),
    ("paper", _("Paper data sheet")),
    ("odk", _("OpenDataKit mobile data capture")),
    ("wamtram", _("WAMTRAM 2 tagging DB")),
    ("ntp-exmouth", _("NTP Access DB Exmouth")),
    ("ntp-broome", _("NTP Access DB Broome")),
    ("cet", _("Cetacean strandings DB")),
    ("pin", _("Pinniped strandings DB")),
    ("reconstructed", _("Reconstructed by WAStD")),
)

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
    ('sat-tag', 'Satellite Relay Data Logger'),  # SRDL
    ('blood-sample', 'Blood Sample'),
    ('biopsy-sample', 'Biopsy Sample'),
    ('stomach-content-sample', 'Stomach Content Sample'),
    ('physical-sample', 'Physical Sample'),
    ('egg-sample', 'Egg Sample'),
    ('qld-monel-a-flipper-tag', 'QLD Monel Series A flipper tag'),         # TRT_IDENTIFICATION_TYPES A
    ('qld-titanium-k-flipper-tag', 'QLD Titanium Series K flipper tag'),         # TRT_IDENTIFICATION_TYPES K
    ('qld-titanium-t-flipper-tag', 'QLD Titanium Series T flipper tag'),         # TRT_IDENTIFICATION_TYPES T
    ('acoustic-tag', 'Acoustic tag'),                           # Acoustic
    ('commonwealth-titanium-flipper-tag', 'Commonwealth titanium flipper tag (old db value)'),      # CA cmlth
    ('cmlth-titanium-flipper-tag', 'Commonwealth titanium flipper tag'),      # CA cmlth
    ('cayman-juvenile-tag', 'Cayman juvenile tag'),   # CT
    ('hawaii-inconel-flipper-tag', 'Hawaii Inst Mar Biol Inconel tag'),  # I
    ('ptt', 'Platform Transmitter Terminal (PTT)'),  # PTT
    ('rototag', 'RotoTag'),  # SFU/FIU
    ('narangebub-nickname', 'Narangebup rehab informal name'),  # RREC
    ('aqwa-nickname', 'AQWA informal name'),  # UWW, from former name UnderWater World
    ('atlantis-nickname', 'Atlantis informal name'),  # ATLANTIS
    ('wa-museum-reptile-registration-number',
        'WA Museum Natural History Reptiles Catalogue Registration Number (old db value)'),  # WAMusR
    ('wam-reptile-registration-number',
        'WA Museum Natural History Reptiles Catalogue Registration Number'),  # WAMusR
    ('genetic-tag', 'Genetic ID sequence'),
    ('other', 'Other'),)

TAG_STATUS_DEFAULT = 'resighted'
TAG_STATUS_APPLIED_NEW = 'applied-new'
TAG_STATUS_CHOICES = (                                          # TRT_TAG_STATES
    ('ordered', 'ordered from manufacturer'),
    ('produced', 'produced by manufacturer'),
    ('delivered', 'delivered to HQ'),
    ('allocated', 'allocated to field team'),
    (TAG_STATUS_APPLIED_NEW, 'applied new'),                    # A1, AE
    (TAG_STATUS_DEFAULT, 're-sighted associated with animal'),  # OX, P, P_OK, RQ, P_ED
    ('reclinched', 're-sighted and reclinched on animal'),       # RC
    ('removed', 'taken off animal'),                            # OO, R
    ('found', 'found detached'),
    ('returned', 'returned to HQ'),
    ('decommissioned', 'decommissioned'),
    ('destroyed', 'destroyed'),
    ('observed', 'observed in any other context, see comments'), )

TAG_STATUS_RESIGHTED = ('resighted', 'reclinched', 'removed')
TAG_STATUS_ON_ANIMAL = (TAG_STATUS_APPLIED_NEW, TAG_STATUS_RESIGHTED)

NEST_TAG_STATUS_CHOICES = (
    (TAG_STATUS_APPLIED_NEW, 'applied new'),
    (TAG_STATUS_DEFAULT, 're-sighted associated with nest'),
)


NA_VALUE = "na"
NA = ((NA_VALUE, "not observed"), )

TAXON_CHOICES_DEFAULT = "Cheloniidae"
TAXON_CHOICES = NA + (
    (TAXON_CHOICES_DEFAULT, "Marine turtles"),
    ("Cetacea", "Whales and Dolphins"),
    ("Pinnipedia", "Pinnipeds"),
    ("Sirenia", "Dugongs"),
    ("Elasmobranchii", "Sharks and Rays"),
    ("Hydrophiinae", "Sea snakes and kraits"), )

TURTLE_SPECIES_DEFAULT = 'cheloniidae-fam'
TURTLE_SPECIES_CHOICES = (
    ('natator-depressus', 'Natator depressus (Flatback turtle)'),
    ('chelonia-mydas', 'Chelonia mydas (Green turtle)'),
    ('eretmochelys-imbricata', 'Eretmochelys imbricata (Hawksbill turtle)'),
    ('caretta-caretta', 'Caretta caretta (Loggerhead turtle)'),
    ('lepidochelys-olivacea', 'Lepidochelys olivacea (Olive ridley turtle)'),
    ('dermochelys-coriacea', 'Dermochelys coriacea (Leatherback turtle)'),
    ('chelonia-mydas-agassazzi', 'Chelonia mydas agassazzi (Black turtle or East Pacific Green)'),
    ('corolla-corolla', 'Corolla corolla (Hatchback turtle)'),
    (TURTLE_SPECIES_DEFAULT, 'Cheloniidae (Unidentified turtle)'),
    # Caretta caretta x Chelonia mydas (Hybrid turtle)
    # Chelonia mydas x Eretmochelys imbricata (Hybrid turtle)
    # Natator depressus x Caretta caretta (Hybrid turtle)
    # Natator depressus x Chelonia mydas (Hybrid turtle)
)
CETACEAN_SPECIES_CHOICES = (
    # dolphins
    ("delphinus-delphis", "Delphinus delphis (Short-beaked common dolphin)"),
    ("grampus-griseus", "Grampus griseus (Risso's dolphin)"),
    ("lagenodelphis-hosei", "Lagenodelphis hosei (Fraser's dolphin)"),
    ("lagenorhynchus-obscurus", "Lagenorhynchus obscurus (Dusky dolphin)"),
    ("orcaella-heinsohni", "Orcaella heinsohni (Australian snubfin dolphin)"),
    ("sousa-sahulensis", "Sousa sahulensis (Australian humpback dolphin)"),
    ("sousa-chinensis", "Sousa chinensis (Chinese white dolphin)"),
    ("stenella-attenuata", "Stenella attenuata (Pantropical spotted dolphin)"),
    ("stenella-coeruleoalba", "Stenella coeruleoalba (Striped dolphin)"),
    ("stenella-longirostris", "Stenella longirostris (Spinner dolphin)"),
    ("stenella-sp", "Stenella sp. (Unidentified spotted dolphin)"),
    ("steno-bredanensis", "Steno bredanensis (Rough-toothed dolphin)"),
    ("tursiops-aduncus", "Tursiops aduncus (Indo-Pacific bottlenose dolphin)"),
    ("tursiops-truncatus", "Tursiops truncatus (Offshore bottlenose dolphin)"),
    ("tursiops-sp", "Tursiops sp. (Unidentified bottlenose dolphin)"),

    ("delphinidae-fam", "Unidentified dolphin"),
    # whales
    ("balaenoptera-acutorostrata", "Balaenoptera acutorostrata (Dwarf minke whale)"),
    ("balaenoptera-bonaerensis", "Balaenoptera bonaerensis (Antarctic minke whale)"),
    ("balaenoptera-borealis", "Balaenoptera borealis (Sei whale)"),
    ("balaenoptera-edeni", "Balaenoptera edeni (Bryde's whale)"),
    ("balaenoptera-musculus", "Balaenoptera musculus (Blue whale)"),
    ("balaenoptera-musculus-brevicauda", "Balaenoptera musculus brevicauda (Pygmy blue whale)"),
    ("balaenoptera-physalus", "Balaenoptera physalus (Fin whale)"),
    ("balaenoptera-omurai", "Balaenoptera omurai (Omura's whale)"),
    ("balaenoptera-sp", "Balaenoptera sp. (Unidentified Balaenoptera)"),
    ("caperea-marginata", "Caperea marginata (Pygmy Right Whale)"),
    ("eubalaena-australis", "Eubalaena australis (Southern right whale)"),
    ("feresa-attenuata", "Feresa attenuata (Pygmy killer whale)"),
    ("globicephala-macrorhynchus", "Globicephala macrorhynchus (Short-finned pilot whale)"),
    ("globicephala-melas", "Globicephala melas (Long-finned pilot whale)"),
    ("globicephala-sp", "Globicephala sp. (Unidentified pilot whale)"),
    ("indopacetus-pacificus", "Indopacetus pacificus (Longman's beaked whale)"),
    ("kogia-breviceps", "Kogia breviceps (Pygmy sperm whale)"),
    ("kogia-sima", "Kogia sima (Dwarf sperm whale)"),
    ("kogia-sp", "Kogia sp. (Unidentified small sperm whale)"),
    ("megaptera-novaeangliae", "Megaptera novaeangliae (Humpback whale)"),
    ("mesoplodon-bowdoini", "Mesoplodon bowdoini (Andew's beaked whale)"),
    ("mesoplodon-densirostris", "Mesoplodon densirostris (Blainville's beaked whale)"),
    ("mesoplodon-grayi", "Mesoplodon grayi (Gray's beaked whale)"),
    ("mesoplodon-hectori", "Mesoplodon hectori (Hector's beaked whale"),
    ("mesoplodon-layardii", "Mesoplodon layardii (Strap-toothed whale)"),
    ("mesoplodon-mirus", "Mesoplodon mirus (True's beaked whale)"),
    ("mesoplodon-sp", "Mesoplodon sp. (Beaked whale)"),
    ("berardius-arnuxii", "Berardius arnuxii (Giant beaked whale)"),
    ("orcinus-orca", "Orcinus orca (Killer whale)"),
    ("peponocephala-electra", "Peponocephala electra (Melon-headed whale)"),
    ("physeter-macrocephalus", "Physeter macrocephalus (Sperm whale)"),
    ("pseudorca-crassidens", "Pseudorca crassidens (False killer whale)"),
    ("ziphius-cavirostris", "Ziphius cavirostris (Cuvier's beaked whale)"),
    ("tasmacetus-shepherdi", "Tasmacetus shepherdi (Shepherd's beaked whale)"),

    ("cetacea", "Unidentified whale"), )

PINNIPED_SPECIES_DEFAULT = 'pinnipedia'
PINNIPED_SPECIES_CHOICES = (
    ("arctocephalus-forsteri", "Arctocephalus forsteri (New Zealand fur seal)"),
    ("neophoca-cinerea", "Neophoca cinerea (Australian sea lion)"),
    ("arctocephalus-tropicalis", "Arctocephalus tropicalis (Subantarctic fur seal)"),
    ("hydrurga-leptonyx", "Hydrurga leptonyx (Leopard seal)"),
    ("lobodon-carcinophagus", "Lobodon carcinophagus (Crabeater seal)"),
    ("mirounga-leonina", "Mirounga leonina (Southern elephant seal)"),
    (PINNIPED_SPECIES_DEFAULT, "Unidentified pinniped"),
)

SEASNAKE_SPECIES_DEFAULT = 'hydrophiinae-subfam'
SEASNAKE_SPECIES_CHOICES = (
    (SEASNAKE_SPECIES_DEFAULT, "Hydrophiinae subfam. (Sea snakes and kraits)"),
    ("acalyptophis-sp", "Acalyptophis sp. (Horned sea snake)"),
    ("aipysurus-sp", "Aipysurus sp. (Olive sea snake)"),
    ("astrotia-sp", "Astrotia sp. (Stokes' sea snake)"),
    ("emydocephalus-sp", "Emydocephalus sp. (Turtlehead sea snake)"),
    ("enhydrina-sp", "Enhydrina sp. (Beaked sea snake)"),
    ("ephalophis-sp", "Ephalophis sp. (Grey's mudsnake)"),
    ("hydrelaps-sp", "Hydrelaps sp. (Port Darwin mudsnake)"),
    ("hydrophis-sp", "Hydrophis sp. (sea snake)"),
    ("kerilia-sp", "Kerilia sp. (Jerdon's sea snake)"),
    ("kolpophis-sp", "Kolpophis sp. (bighead sea snake)"),
    ("lapemis-sp", "Lapemis sp. (Shaw's sea snake)"),
    ("laticauda-sp", "Laticauda sp. (Sea krait)"),
    ("parahydrophis-sp", "Parahydrophis (Northern mangrove sea snake)"),
    ("parapistocalamus-sp", "Parapistocalamus sp. (Hediger's snake)"),
    ("pelamis-sp", "Pelamis sp. (Yellow-bellied sea snake)"),
    ("praescutata-sp", "Praescutata sp. (Sea snake)"),
    ("thalassophis-sp", "Thalassophis sp. (Sea snake)"),
)

SIRENIA_CHOICES = (
    ("dugong-dugon", "Dugong dugon (Dugong)"),
)

SPECIES_CHOICES = NA +\
    TURTLE_SPECIES_CHOICES +\
    CETACEAN_SPECIES_CHOICES +\
    SIRENIA_CHOICES +\
    PINNIPED_SPECIES_CHOICES +\
    SEASNAKE_SPECIES_CHOICES

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
    ("sub-adult", "sub-adult"),
    ("adult-measured", "adult (status determined from carapace and tail measurements)"), )

MAMMAL_MATURITY_CHOICES = (
    ("unweaned", "unweaned immature"),
    ("weaned", "weaned immature"), )

MATURITY_CHOICES = ((NA_VALUE, "unknown maturity"), ) +\
    TURTLE_MATURITY_CHOICES + MAMMAL_MATURITY_CHOICES +\
    (("adult", "adult"), )

HEALTH_D1 = 'alive-then-died'
HEALTH_D2 = 'dead-edible'
HEALTH_D3 = 'dead-organs-intact'
HEALTH_D4 = 'dead-advanced'
HEALTH_D5 = 'dead-mummified'
HEALTH_D6 = 'dead-disarticulated'
DEATH_STAGES = (
    HEALTH_D1, HEALTH_D2, HEALTH_D3, HEALTH_D4, HEALTH_D5, HEALTH_D6)
HEALTH_CHOICES = (
    (NA_VALUE, "unknown health"),
    ('alive', 'alive, healthy'),
    ('alive-injured', 'alive, injured'),
    (HEALTH_D1, 'D1 (alive, then died)'),
    (HEALTH_D2, 'D2 (dead, fresh)'),
    (HEALTH_D3, 'D3 (dead, organs intact)'),
    (HEALTH_D4, 'D4 (dead, organs decomposed)'),
    (HEALTH_D5, 'D5 (dead, mummified)'),
    (HEALTH_D6, 'D6 (dead, disarticulated)'),
    ('other', 'other'),
)

# StrandNet: same as above
# some health status options are confused with management actions
# (disposal, rehab, euth), cause of death
#
# <option value="16">DA - Rescued after disorientation inland by artificial lighting</option>
# <option value="22">DK - Killed for research</option>
# <option value="1">DL - Alive and left to natural processes. Not rescued</option>
# <option value="23">DU - Live but subsequently euthanased</option>
# <option value="2">DZ - Alive and rescued</option></select>

CAUSE_OF_DEATH_CHOICES = NA + (
    ("indeterminate-decomposed", "Indeterminate due to decomposition"),
    ("boat-strike", "Boat strike"),
    ("trauma-human-induced", "Human induced trauma"),
    ("trauma-animal-induced", "Animal induced trauma"),
    ("drowned-entangled-fisheries", "Drowned entangled in fisheries equipment"),
    ("drowned-entangled-infrastructure", "Drowned entangled in infrastructure"),
    ("drowned-entangled-debris", "Drowned entangled in debris"),
    ("drowned-entangled", "Drowned entangled"),
    ("drowned-other", "Drowned"),
    ("fishery-bycatch", "Fishery bycatch"),
    ("handling-accident", "Handling accident"),
    ("car-collision", "Car collision"),
    ("ingested-debris", "Ingested debris"),
    ("harvest", "Harvested for human consumption"),
    ("poisoned", "Poisoned"),
    ("misorientation", "Misorientation on beach"),
    ("natural", "Natural death"),
    ("birthing", "Birthing complications"),
    ("still-born", "Still birth"),
    ("calf-failure-to-thrive", "Calf failed to thrive"),
    ("starved", "Starvation"),
    ("stranded", "Stranding"),
    ("euthanasia-firearm", "Euthanasia by firearm"),
    ("euthanasia-injection", "Euthanasia by injection"),
    ("euthanasia-implosion", "Euthanasia by implosion"),
    ("euthanasia", "Euthanasia"),
    ("predation", "Predation"),
)

CONFIDENCE_CHOICES = NA + (
    ("guess", "Guess based on insuffient evidence"),
    ("expert-opinion", "Expert opinion based on available evidence"),
    ("validated", "Validated by authoritative source"),
)

NESTING_ACTIVITY_CHOICES = (
    ("arriving", "arriving on beach"),
    ("approaching", "approaching nesting site"),
    ("digging-body-pit", "digging body pit"),
    ("excavating-egg-chamber", "excavating egg chamber"),
    ("laying-eggs", "laying eggs"),
    ("filling-in-egg-chamber", "filling in egg chamber"),
    ("filling-in-nest", "filling in nest"),
    ("camouflaging-nest", "camouflaging nest"),
    ("returning-to-water", "returning to water"),
    ("general-breeding-activity", "general breeding activity"),
)

STRANDING_ACTIVITY_CHOICES = (
    ("floating", "floating (dead, sick, unable to dive, drifting in water)"),
    ("beach-washed", "beach washed (dead, sick or stranded on beach/coast)"),
    ("beach-jumped", "beach jumped"),
    ("carcass-tagged-released", "carcass tagged and released"),
    ("carcass-inland", "carcass or butchered remains found removed from coast"),
    ("captivity", "in captivity"),
    ("non-breeding", "general non-breeding activity (swimming, sleeping, feeding, etc.)"),
    ("other", "other activity"),
)

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
    (NA_VALUE, "unknown habitat"),
    ("beach-below-high-water", _("(B) beach below high water mark")),
    ("beach-above-high-water", _("(A) beach above high water mark and dune")),
    ("beach-edge-of-vegetation", _("(E) edge of vegetation")),
    ("in-dune-vegetation", _("(V) inside vegetation")), )

HABITAT_CHOICES = BEACH_POSITION_CHOICES + (
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
    ("below-mean-spring-high-water-mark",
        "below the mean spring high water line or current level of inundation (old db value)"),
    ("below-mshwm", "below the mean spring high water line or current level of inundation"),
    ("lagoon-patch-reef", "lagoon, patch reef"),
    ("lagoon-open-sand", "lagoon, open sand areas"),
    ("mangroves", "mangroves"),
    ("reef-coral", "coral reef"),
    ("reef-crest-front-slope", "reef crest (dries at low water) and front reef slope areas"),
    ("reef-flat", "reef flat, dries at low tide"),
    ("reef-seagrass-flats", "coral reef with seagrass flats"),
    ("reef-rocky", "rocky reef"),
    ("open-water", "open water"),
    ("harbour", "harbour"),
    ("boat-ramp", "boat ramp"),
)

HABITAT_WATER = ("lagoon-patch-reef", "lagoon-open-sand", "mangroves",
                 "reef-coral", "reef-crest-front-slope", "reef-flat",
                 "reef-seagrass-flats", "reef-rocky", "open-water", "harbour")

NEST_AGE_DEFAULT = "unknown"
NEST_AGE_CHOICES = (
    ("old", "(O) old, made before last night"),
    ("fresh", "(F) fresh, made last night"),
    (NEST_AGE_DEFAULT, "(U) unknown age"),
    ("missed", "(M) missed turtle, made within past hours"),
)

NEST_TYPE_DEFAULT = "track-not-assessed"
NEST_TYPE_CHOICES = (
    ("track-not-assessed", "track, not checked for nest"),
    ("false-crawl", "track without nest"),
    ("successful-crawl", "track with nest"),
    ("track-unsure", "track, checked for nest, unsure if nest"),
    ("nest", "nest, unhatched, no track"),         # egg counts, putting eggs back
    ("hatched-nest", "nest, hatched"),   # hatching and emergence success
    ("body-pit", "body pit, no track"),
)

OBSERVATION_CHOICES = (
    (NA_VALUE, "NA"),
    ("absent", "Confirmed absent"),
    ("present", "Confirmed present"),
)

OBSERVATION_ICONS = {
    NA_VALUE: "fa fa-question-circle-o",
    "absent": "fa fa-times",
    "present": "fa fa-check"}

PHOTO_CHOICES = NA + (("see photos", "See attached photos for details"),)

PHOTO_ICONS = {
    NA_VALUE: "fa fa-question-circle-o",
    "see photos": "fa fa-check"}

ACCURACY_CHOICES = (
    ("1", "To nearest 1 mm"),
    ("5", "To nearest 5 mm"),
    ("10", "To nearest 1 cm"),              # Default for stranding "measured"
    ("100", "To nearest 10 cm"),            # Default for stranding "estimated"
    ("1000", "To nearest 1 m or 1 kg"),
    ("10000", "To nearest 10 m or 10 kg"),
)

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
    ("fresh", "fresh"),
)

NEST_DAMAGE_DEFAULT = "turtle"
NEST_DAMAGE_CHOICES = (
    (NEST_DAMAGE_DEFAULT, "(A)nother turtle"),
    ("bandicoot", "(Ba)ndicoot predation"),
    ("bird", "(Bi)rd predation"),
    ("crab", "(Cr)ab predation"),
    ("croc", "(Cr)oc predation"),
    ("cyclone", "(Cy)clone disturbance"),
    ("dingo", "(Di)ngo predation"),
    ("dog", "(Do)g predation"),
    ("fox", "(F)ox predation"),
    ("goanna", "(G)oanna predation"),
    ("human", "(Hu)man"),
    ("pig", "(P)ig predation"),
    ("tide", "(Ti)dal disturbance"),
    ("vehicle", "(V)ehicle damage"),
    ("unknown", "(U)nknown"),
    ("other", "(O)ther identifiable (see comments)"),
)
# End lookups ----------------------------------------------------------------#


def encounter_media(instance, filename):
    """Return an upload file path for an encounter media attachment."""
    if not instance.encounter.id:
        instance.encounter.save()
    return 'encounter/{0}/{1}'.format(instance.encounter.source_id, filename)


def expedition_media(instance, filename):
    """Return an upload file path for an expedition media attachment."""
    if not instance.expedition.id:
        instance.expedition.save()
    return 'expedition/{0}/{1}'.format(instance.expedition.id, filename)


def survey_media(instance, filename):
    """Return an upload path for survey media."""
    if not instance.id:
        instance.save()
    return 'survey/{0}/{1}'.format(instance.id, filename)


# Abstract models ------------------------------------------------------------#
class QualityControl(models.Model):
    """QA status levels and django-fsm transitions."""

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

    status = FSMField(
        default=STATUS_NEW,
        choices=STATUS_CHOICES,
        verbose_name=_("QA Status"))

    class Meta:
        """Class opts."""

        abstract = True

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


# Spatial models -------------------------------------------------------------#
@python_2_unicode_compatible
class Area(geo_models.Model):
    """An area with a polygonal extent.

    This model accommodates anything with a polygonal extent, providing:

    * Area type (to classify different kinds of areas)
    * Area name must be unique within area type
    * Polygonal extent of the area

    Some additional fields are populated behind the scenes at each save and
    serve to cache low churn, high use content:

    * centroid: useful for spatial analysis and location queries
    * northern extent: useful to sort by latitude
    * as html: an HTML map popup
    """

    AREATYPE_MPA = 'MPA'
    AREATYPE_LOCALITY = 'Locality'
    AREATYPE_SITE = 'Site'
    AREATYPE_DBCA_REGION = 'Region'
    AREATYPE_DBCA_DISTRICT = 'District'

    AREATYPE_CHOICES = (
        (AREATYPE_MPA, "MPA"),
        (AREATYPE_LOCALITY, "Locality"),
        (AREATYPE_SITE, "Site"),
        (AREATYPE_DBCA_REGION, "DBCA Region"),
        (AREATYPE_DBCA_DISTRICT, "DBCA District"),
    )

    area_type = models.CharField(
        max_length=300,
        verbose_name=_("Area type"),
        default=AREATYPE_SITE,
        choices=AREATYPE_CHOICES,
        help_text=_("The area type."), )

    name = models.CharField(
        max_length=1000,
        verbose_name=_("Area Name"),
        help_text=_("The name of the area."),)

    centroid = geo_models.PointField(
        srid=4326,
        editable=False,
        blank=True, null=True,
        verbose_name=_("Centroid"),
        help_text=_("The centroid is a simplified presentation of the Area."))

    northern_extent = models.FloatField(
        verbose_name=_("Northernmost latitude"),
        editable=False,
        blank=True, null=True,
        help_text=_("The northernmost latitude serves to sort areas."),)

    length_surveyed_m = models.DecimalField(
        max_digits=10, decimal_places=0,
        verbose_name=_("Surveyed length [m]"),
        blank=True, null=True,
        help_text=_("The length of meters covered by a survey of this area. "
                    "E.g., the meters of high water mark along a beach."),
    )

    length_survey_roundtrip_m = models.DecimalField(
        max_digits=10, decimal_places=0,
        verbose_name=_("Survey roundtrip [m]"),
        blank=True, null=True,
        help_text=_("The total length of meters walked during an end to end "
                    "survey of this area."),
    )

    as_html = models.TextField(
        verbose_name=_("HTML representation"),
        blank=True, null=True, editable=False,
        help_text=_("The cached HTML representation for display purposes."),)

    geom = geo_models.PolygonField(
        srid=4326,
        verbose_name=_("Location"),
        help_text=_("The exact extent of the area as polygon in WGS84."))

    class Meta:
        """Class options."""

        ordering = ["-northern_extent", "name"]
        unique_together = ("area_type", "name")
        verbose_name = "Area"
        verbose_name_plural = "Areas"

    def save(self, *args, **kwargs):
        """Cache centroid and northern extent."""
        self.as_html = self.get_popup
        if not self.northern_extent:
            self.northern_extent = self.derived_northern_extent
        if not self.centroid:
            self.centroid = self.derived_centroid
        super(Area, self).save(*args, **kwargs)

    def __str__(self):
        """The unicode representation."""
        return "{0} {1}".format(self.area_type, self.name, )

    @property
    def derived_centroid(self):
        """The centroid, derived from the polygon."""
        return self.geom.centroid or None

    @property
    def derived_northern_extent(self):
        """The northern extent, derived from the polygon."""
        return self.geom.extent[3] or None

    @property
    def get_popup(self):
        """Generate HTML popup content."""
        t = loader.get_template("popup/{0}.html".format(self._meta.model_name))
        c = dict(original=self)
        return mark_safe(t.render(c))

    @property
    def leaflet_title(self):
        """A title for leaflet map markers."""
        return self.__str__()

    @property
    def absolute_admin_url(self):
        """Return the absolute admin change URL."""
        return reverse('admin:{0}_{1}_change'.format(
            self._meta.app_label, self._meta.model_name), args=[self.pk])

    @property
    def all_encounters_url(self):
        """All Encounters within this Area."""
        return '/admin/observations/encounter/?{0}__id__exact={1}'.format(
            "site" if self.area_type == Area.AREATYPE_SITE else "area",
            self.pk,
        )

    @property
    def animal_encounters_url(self):
        """The admin URL for AnimalEncounters within this Area."""
        return '/admin/observations/animalencounter/?{0}__id__exact={1}'.format(
            "site" if self.area_type == Area.AREATYPE_SITE else "area",
            self.pk,
        )

    def make_rest_listurl(self, format='json'):
        """Return the API list URL in given format (default: JSON).

        Permissible formats depend on configured renderers:
        api (human readable HTML), csv, json, jsonp, yaml, latex (PDF).
        """
        return rest_reverse(self._meta.model_name + '-list',
                            kwargs={'format': format})

    def make_rest_detailurl(self, format='json'):
        """Return the API detail URL in given format (default: JSON).

        Permissible formats depend on configured renderers:
        api (human readable HTML), csv, json, jsonp, yaml, latex (PDF).
        """
        return rest_reverse(self._meta.model_name + '-detail',
                            kwargs={'pk': self.pk, 'format': format})


@python_2_unicode_compatible
class SiteVisitStartEnd(geo_models.Model):
    """A start or end point to a site visit."""

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
        help_text=_("The ID of the record in the original source, or "
                    "a newly allocated ID if left blank. Delete and save "
                    "to regenerate this ID."), )

    datetime = models.DateTimeField(
        verbose_name=_("Observation time"),
        help_text=_("Local time (no daylight savings), stored as UTC."))

    location = geo_models.PointField(
        srid=4326,
        verbose_name=_("Location"),
        help_text=_("The observation location as point in WGS84"))

    type = models.CharField(
        max_length=300,
        verbose_name=_("Type"),
        choices=(("start", "start"), ("end", "end")),
        default="start",
        help_text=_("Start of end of site visit?"),)

    # media attachment

    def __str__(self):
        """The unicode representation."""
        return "Site visit start or end on {0}".format(
            self.datetime.isoformat())


@python_2_unicode_compatible
class Expedition(PolymorphicModel, geo_models.Model):
    """An endeavour of a team to a location within a defined time range."""

    site = models.ForeignKey(
        Area,
        on_delete=models.PROTECT,
        blank=True, null=True,
        verbose_name=_("Surveyed area"),
        help_text=_("The entire surveyed area."), )

    started_on = models.DateTimeField(
        verbose_name=_("Site entered on"),
        blank=True, null=True,
        help_text=_("The datetime of entering the site, shown as local time "
                    "(no daylight savings), stored as UTC."))

    finished_on = models.DateTimeField(
        verbose_name=_("Site left on"),
        blank=True, null=True,
        help_text=_("The datetime of leaving the site, shown as local time "
                    "(no daylight savings), stored as UTC."))

    comments = models.TextField(
        verbose_name=_("Comments"),
        blank=True, null=True,
        help_text=_("Describe any circumstances affecting data collection, "
                    "e.g. days without surveys."), )

    team = models.ManyToManyField(
        User,
        related_name="expedition_team")

    def __str__(self):
        """The unicode representation."""
        return "Expedition {0} to {1} from {2} to {3}".format(
            self.pk,
            "unknown site" if not self.site else self.site.name,
            "na" if not self.started_on else self.started_on.isoformat(),
            "na" if not self.finished_on else self.finished_on.isoformat())

    @property
    def site_visits(self):
        """Return a QuerySet of site visits."""
        return SiteVisit.objects.filter(
            site__geom__contained=self.site.geom,
            started_on__gte=self.started_on,
            finished_on__lte=self.finished_on)


@python_2_unicode_compatible
class SiteVisit(Expedition):
    """A visit to one site by a team of field workers collecting data."""

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
        help_text=_("The ID of the start point in the original source, or "
                    "a newly allocated ID if left blank. Delete and save "
                    "to regenerate this ID."), )

    end_source_id = models.CharField(
        max_length=1000,
        blank=True, null=True,
        verbose_name=_("Source ID of end point"),
        help_text=_("The ID of the record in the original source, or "
                    "a newly allocated ID if left blank. Delete and save "
                    "to regenerate this ID."), )

    start_location = geo_models.PointField(
        srid=4326,
        blank=True, null=True,
        verbose_name=_("Start location"),
        help_text=_("The start location as point in WGS84"))

    end_location = geo_models.PointField(
        srid=4326,
        blank=True, null=True,
        verbose_name=_("End location"),
        help_text=_("The end location as point in WGS84"))

    transect = geo_models.LineStringField(
        srid=4326,
        blank=True, null=True,
        verbose_name=_("Transect line"),
        help_text=_("The surveyed path as LineString in WGS84, optional."))

    def __str__(self):
        """The unicode representation."""
        return "Site Visit {0} of {1} from {2} to {3}".format(
            self.pk,
            "unknown site" if not self.site else self.site.name,
            "na" if not self.started_on else self.started_on.isoformat(),
            "na" if not self.finished_on else self.finished_on.isoformat())

    @property
    def encounters(self):
        """Return the QuerySet of all Encounters within this SiteVisit."""
        return Encounter.objects.filter(
            where__contained=self.site.geom,
            when__gte=self.started_on,
            when__lte=self.finished_on)

    def claim_encounters(self):
        """Update Encounters within this SiteVisit with reference to self."""
        self.encounters.update(site_visit=self)

    def claim_end_points(self):
        """TODO Claim SiteVisitEnd."""
        pass


@python_2_unicode_compatible
class FieldMediaAttachment(models.Model):
    """A media attachment to an Expedition or Survey."""

    MEDIA_TYPE_CHOICES = (
        ('data_sheet', _('Data sheet')),
        ('journal', _('Field journal')),
        ('communication', _('Communication record')),
        ('photograph', _('Photograph')),
        ('other', _('Other')), )

    expedition = models.ForeignKey(
        Expedition,
        on_delete=models.CASCADE,
        verbose_name=_("Expedition"),
        help_text=_("Surveys can be conducted during an expedition."), )

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
        upload_to=expedition_media,
        max_length=500,
        verbose_name=_("File attachment"),
        help_text=_("Upload the file"),)

    def __str__(self):
        """The unicode representation."""
        return "Attachment {0} {1} for {2}".format(
            self.pk, self.title, self.expedition.__str__())

    @property
    def filepath(self):
        """Path to file."""
        return force_text(self.attachment.file)


@python_2_unicode_compatible
class Survey(QualityControl, geo_models.Model):
    """A visit to one site by a team of field workers collecting data."""

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
        help_text=_("The ID of the start point in the original source."), )

    device_id = models.CharField(
        max_length=1000,
        blank=True, null=True,
        verbose_name=_("Device ID"),
        help_text=_("The ID of the recording device, if available."), )

    site = models.ForeignKey(
        Area,
        on_delete=models.PROTECT,
        blank=True, null=True,
        verbose_name=_("Surveyed site"),
        help_text=_("The surveyed site, if known."), )

    transect = geo_models.LineStringField(
        srid=4326,
        blank=True, null=True,
        verbose_name=_("Transect line"),
        help_text=_(
            "The surveyed path as LineString in WGS84, optional."
            " E.g. automatically captured by form Track Tally."))

    reporter = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name=_("Recorded by"),
        blank=True, null=True,
        help_text=_(
            "The person who captured the start point, "
            "ideally this person also recoreded the encounters and end point."))

    start_location = geo_models.PointField(
        srid=4326,
        blank=True, null=True,
        verbose_name=_("Survey start point"),
        help_text=_("The start location as point in WGS84."))

    start_time = models.DateTimeField(
        verbose_name=_("Survey start time"),
        blank=True, null=True,
        help_text=_("The datetime of entering the site, shown as local time "
                    "(no daylight savings), stored as UTC."
                    " The time of 'feet in the sand, start recording encounters'."))

    start_photo = models.FileField(
        upload_to=survey_media,
        blank=True, null=True,
        max_length=500,
        verbose_name=_("Site photo start"),
        help_text=_("Site conditions at start of survey."),)

    start_comments = models.TextField(
        verbose_name=_("Comments at start"),
        blank=True, null=True,
        help_text=_("Describe any circumstances affecting data collection, "
                    "e.g. days without surveys."), )

    end_source_id = models.CharField(
        max_length=1000,
        blank=True, null=True,
        verbose_name=_("Source ID of end point"),
        help_text=_("The ID of the record in the original source."), )

    end_device_id = models.CharField(
        max_length=1000,
        blank=True, null=True,
        verbose_name=_("End Device ID"),
        help_text=_("The ID of the recording device which captured the end point, if available."), )

    end_location = geo_models.PointField(
        srid=4326,
        blank=True, null=True,
        verbose_name=_("Survey end point"),
        help_text=_("The end location as point in WGS84."))

    end_time = models.DateTimeField(
        verbose_name=_("Survey end time"),
        blank=True, null=True,
        help_text=_("The datetime of leaving the site, shown as local time "
                    "(no daylight savings), stored as UTC."
                    " The time of 'feet in the sand, done recording encounters.'"))

    end_photo = models.FileField(
        upload_to=expedition_media,
        blank=True, null=True,
        max_length=500,
        verbose_name=_("Site photo end"),
        help_text=_("Site conditions at end of survey."),)

    end_comments = models.TextField(
        verbose_name=_("Comments at finish"),
        blank=True, null=True,
        help_text=_("Describe any circumstances affecting data collection, "
                    "e.g. days without surveys."), )

    production = models.BooleanField(
        default=True,
        verbose_name=_("Production run"),
        help_text=_("Whether the survey is a real (production) survey, or a training survey."),
    )

    team = models.ManyToManyField(
        User,
        blank=True,
        related_name="survey_team",
        help_text=_(
            "Additional field workers, apart from the reporter,"
            " who assisted with data collection."))

    class Meta:
        """Class options."""

        ordering = ["start_location", "start_time"]
        unique_together = ("source", "source_id")

    def __str__(self):
        """The unicode representation."""
        return "Survey {0} of {1} from {2} to {3}".format(
            self.pk,
            "unknown site" if not self.site else self.site.name,
            "na" if not self.start_time else self.start_time.astimezone(tz.tzlocal()).strftime("%Y-%m-%d %H:%M %Z"),
            "na" if not self.end_time else self.end_time.astimezone(tz.tzlocal()).strftime("%Y-%m-%d %H:%M"))

    @property
    def absolute_admin_url(self):
        """Return the absolute admin change URL."""
        return reverse('admin:{0}_{1}_change'.format(
            self._meta.app_label, self._meta.model_name), args=[self.pk])

    @property
    def encounters(self):
        """Return the QuerySet of all Encounters within this SiteVisit unless it's a training run."""
        if not self.production:
            return None
        if not self.end_time:
            logger.info("[wastd.observations.models.survey.encounters] No end_time set, can't filter Encounters")
            return None
        elif not self.site:
            logger.info("[wastd.observations.models.survey.encounters] No site set, can't filter Encounters")
            return None
        else:
            e = Encounter.objects.filter(
                where__contained=self.site.geom,
                when__gte=self.start_time,
                when__lte=self.end_time)
            logger.info("[Survey.encounters] {0} found {1} Encounters".format(self, len(e)))
            return e


def guess_site(survey_instance):
    """Return the first Area containing the start_location or None."""
    return Area.objects.filter(
        area_type=Area.AREATYPE_SITE,
        geom__contains=survey_instance.start_location).first()


def claim_end_points(survey_instance):
    """Claim SurveyEnd.

    The first SurveyEnd with the matching site,
    and an end_time within six hours after start_time is used
    to set corresponding end_location, end_time, end_comments,
    end_photo and end_source_id.

    Since the end point could be taken with a different device (e.g.
    if primary device malfunctions), we will not filter down to
    the same device_id.

    If no SurveyEnd is found and no end_time is set, the end_time is set to
    start_time plus six hours. This should allow the survey to claim its Encounters.

    TODO we could be a bit cleverer and find the latest encounter on the same day and site.
    """
    se = SurveyEnd.objects.filter(
        site=survey_instance.site,
        # device_id=survey_instance.device_id,
        end_time__gte=survey_instance.start_time,
        end_time__lte=survey_instance.start_time + timedelta(hours=6)
    ).first()
    if se:
        survey_instance.end_location = se.end_location
        survey_instance.end_time = se.end_time
        survey_instance.end_comments = se.end_comments
        survey_instance.end_photo = se.end_photo
        survey_instance.end_source_id = se.source_id
        survey_instance.end_device_id = se.device_id
    else:
        if not survey_instance.end_time:
            survey_instance.end_time = survey_instance.start_time + timedelta(hours=6)
            survey_instance.end_comments = "[NEEDS QA][Missing SiteVisitEnd] Survey end guessed."
            logger.info("[Survey.claim_end_points] Missing SiteVisitEnd for Survey"
                        " {0}".format(survey_instance))


def claim_encounters(survey_instance):
    """Update Encounters within this Survey to reference survey=self."""
    enc = survey_instance.encounters
    if enc:
        enc.update(survey=survey_instance)
        logger.info("[wastd.observations.models.claim_encounters] "
                    "Survey {0} claimed {1} Encounters".format(survey_instance, len(enc)))


@receiver(pre_save, sender=Survey)
def survey_pre_save(sender, instance, buffer_mins=30, *args, **kwargs):
    """Survey: Claim site, end point, adjust end time if encounters already claimed."""
    if instance.status == Survey.STATUS_NEW and not instance.site:
        instance.site = guess_site(instance)
    if instance.status == Survey.STATUS_NEW and not instance.end_time:
        claim_end_points(instance)
    if instance.end_time == instance.start_time + timedelta(hours=6):
        et = instance.end_time
        if instance.encounters:
            instance.end_time = instance.encounters.last().when + timedelta(minutes=buffer_mins)
            msg = ("[survey_pre_save] End time adjusted from {0} to {1}, "
                   "{2} minutes after last of {3} encounters.").format(
                et, instance.end_time, buffer_mins, len(instance.encounters))
        else:
            instance.end_time = instance.start_time + timedelta(minutes=buffer_mins)
            msg = ("[survey_pre_save] End time adjusted from {0} to {1}, "
                   "{2} minutes after the start of the survey. "
                   "No encounters found.").format(et, instance.end_time, buffer_mins)
        instance.end_comments = msg
        logger.info(msg)


@receiver(post_save, sender=Survey)
def survey_post_save(sender, instance, *args, **kwargs):
    """Survey: Claim encounters."""
    claim_encounters(instance)


@python_2_unicode_compatible
class SurveyEnd(geo_models.Model):
    """A visit to one site by a team of field workers collecting data."""

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
        help_text=_("The ID of the start point in the original source."), )

    device_id = models.CharField(
        max_length=1000,
        blank=True, null=True,
        verbose_name=_("Device ID"),
        help_text=_("The ID of the recording device, if available."), )

    reporter = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name=_("Recorded by"),
        blank=True, null=True,
        help_text=_(
            "The person who captured the start point, "
            "ideally this person also recoreded the encounters and end point."))

    site = models.ForeignKey(
        Area,
        on_delete=models.PROTECT,
        blank=True, null=True,
        verbose_name=_("Surveyed site"),
        help_text=_("The surveyed site, if known."), )

    end_location = geo_models.PointField(
        srid=4326,
        blank=True, null=True,
        verbose_name=_("Survey end point"),
        help_text=_("The end location as point in WGS84."))

    end_time = models.DateTimeField(
        verbose_name=_("Survey end time"),
        blank=True, null=True,
        help_text=_("The datetime of leaving the site, shown as local time "
                    "(no daylight savings), stored as UTC."
                    " The time of 'feet in the sand, done recording encounters.'"))

    end_photo = models.FileField(
        upload_to=survey_media,
        max_length=500,
        verbose_name=_("Site photo end"),
        help_text=_("Site conditions at end of survey."),)

    end_comments = models.TextField(
        verbose_name=_("Comments at finish"),
        blank=True, null=True,
        help_text=_("Describe any circumstances affecting data collection, "
                    "e.g. days without surveys."), )

    class Meta:
        """Class options."""

        ordering = ["end_location", "end_time"]
        unique_together = ("source", "source_id")

    def save(self, *args, **kwargs):
        """Guess site."""
        self.site = self.guess_site
        super(SurveyEnd, self).save(*args, **kwargs)

    def __str__(self):
        """The unicode representation."""
        return "SurveyEnd {0} at {1} on {2}".format(
            self.pk,
            "na" if not self.site else self.site,
            "na" if not self.end_time else self.end_time.isoformat())

    @property
    def guess_site(self):
        """Return the first Area containing the start_location or None."""
        candidates = Area.objects.filter(
            area_type=Area.AREATYPE_SITE,
            geom__contains=self.end_location)
        return None if not candidates else candidates.first()


# Utilities ------------------------------------------------------------------#
@receiver(pre_delete)
def delete_observations(sender, instance, **kwargs):
    """Delete Observations before deleting an Encounter.

    See https://github.com/django-polymorphic/django-polymorphic/issues/34
    """
    if sender == Encounter:
        [obs.delete() for obs in instance.observation_set.all()]


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

    ENCOUNTER_STRANDING = 'stranding'
    ENCOUNTER_TAGGING = 'tagging'
    ENCOUNTER_INWATER = 'inwater'
    ENCOUNTER_NEST = 'nest'
    ENCOUNTER_TRACKS = 'tracks'
    ENCOUNTER_TAG = 'tag-management'
    ENCOUNTER_LOGGER = 'logger'
    ENCOUNTER_OTHER = 'other'

    ENCOUNTER_TYPES = (
        (ENCOUNTER_STRANDING, "Stranding"),
        (ENCOUNTER_TAGGING, "Tagging"),
        (ENCOUNTER_NEST, "Nest"),
        (ENCOUNTER_TRACKS, "Tracks"),
        (ENCOUNTER_INWATER, "In water"),
        (ENCOUNTER_TAG, "Tag Management"),
        (ENCOUNTER_LOGGER, "Logger"),
        (ENCOUNTER_OTHER, "Other")
    )

    LEAFLET_ICON = {
        ENCOUNTER_STRANDING: "exclamation-circle",
        ENCOUNTER_TAGGING: "tags",
        ENCOUNTER_NEST: "home",
        ENCOUNTER_TRACKS: "truck",
        ENCOUNTER_TAG: "cog",
        ENCOUNTER_INWATER: "tint",
        ENCOUNTER_LOGGER: "tablet",
        ENCOUNTER_OTHER: "question-circle"
    }

    LEAFLET_COLOUR = {
        ENCOUNTER_STRANDING: 'darkred',
        ENCOUNTER_TAGGING: 'blue',
        ENCOUNTER_INWATER: 'blue',
        ENCOUNTER_NEST: 'green',
        ENCOUNTER_TRACKS: 'cadetblue',
        ENCOUNTER_TAG: 'darkpuple',
        ENCOUNTER_LOGGER: 'orange',
        ENCOUNTER_OTHER: 'purple'
    }

    survey = models.ForeignKey(
        Survey,
        on_delete=models.PROTECT,
        null=True, blank=True,
        verbose_name=_("Survey"),
        help_text=_("The survey during which this encounter happened."),)

    area = models.ForeignKey(
        Area,
        on_delete=models.PROTECT,
        blank=True, null=True,
        verbose_name=_("Area"),
        related_name="encounter_area",
        help_text=_("The general area this encounter took place in."), )

    site = models.ForeignKey(
        Area,
        on_delete=models.PROTECT,
        blank=True, null=True,
        verbose_name=_("Surveyed site"),
        related_name="encounter_site",
        help_text=_("The surveyed site, if known."), )

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
        help_text=_("The ID of the record in the original source, or "
                    "a newly allocated ID if left blank. Delete and save "
                    "to regenerate this ID."), )

    status = FSMField(
        default=STATUS_NEW,
        choices=STATUS_CHOICES,
        verbose_name=_("QA Status"))

    where = geo_models.PointField(
        srid=4326,
        verbose_name=_("Observed at"),
        help_text=_("The observation location as point in WGS84"))

    when = models.DateTimeField(
        verbose_name=_("Observed on"),
        help_text=_("The observation datetime, shown as local time "
                    "(no daylight savings), stored as UTC."))

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
        on_delete=models.PROTECT,
        verbose_name=_("Measured by"),
        related_name="observer",
        help_text=_("The person who executes the measurements, "
                    "source of measurement bias"))

    reporter = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name=_("Recorded by"),
        related_name="reporter",
        help_text=_("The person who writes the data sheet in the field, "
                    "source of handwriting and spelling errors"))

    as_html = models.TextField(
        verbose_name=_("HTML representation"),
        blank=True, null=True, editable=False,
        help_text=_("The cached HTML representation for display purposes."),)

    as_latex = models.TextField(
        verbose_name=_("Latex fragment"),
        blank=True, null=True, editable=False,
        help_text=_("The cached Latex fragment for reporting purposes."),)

    encounter_type = models.CharField(
        max_length=300,
        blank=True, null=True, editable=False,
        verbose_name=_("Encounter type"),
        default=ENCOUNTER_STRANDING,
        choices=ENCOUNTER_TYPES,
        help_text=_("The primary concern of this encounter."), )

    comments = models.TextField(
        verbose_name=_("Comments"),
        blank=True, null=True,
        help_text=_("Comments"), )

    class Meta:
        """Class options."""

        ordering = ["when", "where"]
        unique_together = ("source", "source_id")
        verbose_name = "Encounter"
        verbose_name_plural = "Encounters"
        get_latest_by = "when"
        # base_manager_name = 'base_objects'  # fix delete bug

    @property
    def opts(self):
        """Make _meta accessible from templates."""
        return self._meta

    def __str__(self):
        """The unicode representation."""
        return "Encounter {0} on {1} by {2}".format(self.pk, self.when, self.observer)

    # -------------------------------------------------------------------------
    # URLs
    @property
    def absolute_admin_url(self):
        """Return the absolute admin change URL."""
        return reverse('admin:{0}_{1}_change'.format(
            self._meta.app_label, self._meta.model_name), args=[self.pk])

    def make_rest_listurl(self, format='json'):
        """Return the API list URL in given format (default: JSON).

        Permissible formats depend on configured renderers:
        api (human readable HTML), csv, json, jsonp, yaml, latex (PDF).
        """
        return rest_reverse(self._meta.model_name + '-list',
                            kwargs={'format': format})

    def make_rest_detailurl(self, format='json'):
        """Return the API detail URL in given format (default: JSON).

        Permissible formats depend on configured renderers:
        api (human readable HTML), csv, json, jsonp, yaml, latex (PDF).
        """
        return rest_reverse(self._meta.model_name + '-detail',
                            kwargs={'pk': self.pk, 'format': format})

    # -------------------------------------------------------------------------
    # Derived properties
    @property
    def leaflet_title(self):
        """A string for Leaflet map marker titles. Cache me as field."""
        return "{0} {1} {2}".format(
            '' if not self.when else self.when.year,
            self.get_encounter_type_display(),
            self.name or '')

    @property
    def leaflet_icon(self):
        """Return the Fontawesome icon class for the encounter type."""
        return(Encounter.LEAFLET_ICON[self.encounter_type])

    @property
    def leaflet_colour(self):
        """Return the Leaflet.awesome-markers colour for the encounter type."""
        return (Encounter.LEAFLET_COLOUR[self.encounter_type])

    @property
    def tx_logs(self):
        """A list of dicts of QA timestamp, status and operator."""
        return [dict(timestamp=log.timestamp.isoformat(),
                     status=log.state,
                     operator=log.by.name)
                for log in StateLog.objects.for_(self)]

    @property
    def get_encounter_type(self):
        """Infer the encounter type.

        "Track" encounters have a TrackTallyObservation, those who don't have
        one but involve a TagObservation are tag management encounters (tag
        orders, distribution, returns, decommissioning).
        Lastly, the catch-all is "other" but complete records should not end up
        as such.
        """
        if self.observation_set.instance_of(TrackTallyObservation).exists():
            return self.ENCOUNTER_TRACKS
        elif self.observation_set.instance_of(TagObservation).exists():
            return self.ENCOUNTER_TAG
        else:
            return self.ENCOUNTER_OTHER

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
            self.when.astimezone(tz.tzlocal()).strftime("%Y-%m-%d %H:%M %Z"),
            force_text(round(self.longitude, 4)).replace(".", "-"),
            force_text(round(self.latitude, 4)).replace(".", "-"),
        ]))

    @property
    def date(self):
        """Return the date component of Encounter.when."""
        return self.when.date()

    @property
    def date_string(self):
        """Return the date as string."""
        return str(self.when.date())

    @property
    def datetime(self):
        """Return the full datetime of the Encounter."""
        return self.when

    def save(self, *args, **kwargs):
        """Cache popup, encounter type and source ID.

        The popup content changes when fields change, and is expensive to build.
        As it is required ofen and under performance-critical circumstances -
        populating the home screen with lots of popups - is is re-calculated
        whenever the contents change (on save) rather when it is required for
        display.

        The source ID will be auto-generated from ``short_name`` (if not set)
        but is not guaranteed to be unique.
        The User will be prompted to provide a unique source ID if necessary,
        e.g. by appending a running number.
        The source ID can be re-created by deleting it and re-saving the object.

        The encounter type is inferred from the type of attached Observations.
        This logic is overridden in subclasses.
        """
        if not self.source_id:
            self.source_id = self.short_name
        if (not self.name) and self.inferred_name:
            self.name = self.inferred_name
        if not self.site:
            self.site = self.guess_site
        if not self.area:
            self.area = self.guess_area
        self.encounter_type = self.get_encounter_type
        self.as_html = self.get_popup()
        self.as_latex = self.get_latex()
        super(Encounter, self).save(*args, **kwargs)

    # Name -------------------------------------------------------------------#
    @property
    def guess_site(self):
        """Return the first Area containing the start_location or None."""
        candidates = Area.objects.filter(
            area_type=Area.AREATYPE_SITE,
            geom__contains=self.where)
        return None if not candidates else candidates.first()

    @property
    def guess_area(self):
        """Return the first Area containing the start_location or None."""
        candidates = Area.objects.filter(
            area_type=Area.AREATYPE_LOCALITY,
            geom__contains=self.where)
        return None if not candidates else candidates.first()

    def set_name(self, name):
        """Set the animal name to a given value."""
        self.name = name
        self.save()
        logger.info("{0} name set to {1}".format(self.__str__(), name))

    @property
    def inferred_name(self):
        """Return the inferred name from related new capture if existing."""
        # TODO less dirty
        try:
            return [enc.name
                    for enc in self.related_encounters
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
                new_tags, without=known_enc)
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

    # HTML popup -------------------------------------------------------------#
    @property
    def wkt(self):
        """Return the point coordinates as Well Known Text (WKT)."""
        return self.where.wkt

    def get_popup(self):
        """Generate HTML popup content."""
        t = loader.get_template("popup/{0}.html".format(self._meta.model_name))
        # c = Context({"original": self})
        return mark_safe(t.render({"original": self}))

    def get_report(self):
        """Generate an HTML report of the Encounter."""
        t = loader.get_template("reports/{0}.html".format(self._meta.model_name))
        # c = Context({"original": self})
        return mark_safe(t.render({"original": self}))

    def get_latex(self):
        """Generate a Latex fragment of the Encounter."""
        t = loader.get_template("latex/fragments/{0}.tex".format(self._meta.model_name))
        # c = Context({"original": self})
        return mark_safe(t.render({"original": self}))

    @property
    def observations(self):
        """Return Observations as list."""
        return self.observation_set.all()

    @property
    def latitude(self):
        """Return the WGS 84 DD latitude."""
        return self.where.y

    @property
    def longitude(self):
        """Return the WGS 84 DD longitude."""
        return self.where.x

    @property
    def crs(self):
        """Return the location CRS."""
        return self.where.srs.name

    @property
    def status_label(self):
        """Return the boostrap tag-* CSS label flavour for the QA status."""
        return Encounter.STATUS_LABELS[self.status]

    @property
    def photographs(self):
        """Return the URLs of all attached photograph or none."""
        try:
            return list(
                self.observation_set.instance_of(
                    MediaAttachment).filter(
                        mediaattachment__media_type="photograph"))
        except:
            return None

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

    Turtle Strandings are encounters of turtles
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
        default=NA_VALUE,
        help_text=_("The species of the animal."), )

    sex = models.CharField(
        max_length=300,
        verbose_name=_("Sex"),
        choices=SEX_CHOICES,
        default=NA_VALUE,
        help_text=_("The animal's sex."), )

    maturity = models.CharField(
        max_length=300,
        verbose_name=_("Maturity"),
        choices=MATURITY_CHOICES,
        default=NA_VALUE,
        help_text=_("The animal's maturity."), )

    health = models.CharField(
        max_length=300,
        verbose_name=_("Health status"),
        choices=HEALTH_CHOICES,
        default=NA_VALUE,
        help_text=_("On a scale from the Fresh Prince of Bel Air to 80s Hair "
                    "Metal: how dead and decomposed is the animal?"), )

    activity = models.CharField(
        max_length=300,
        verbose_name=_("Activity"),
        choices=ACTIVITY_CHOICES,
        default=NA_VALUE,
        help_text=_("The animal's activity at the time of observation."), )

    behaviour = models.TextField(
        verbose_name=_("Condition and behaviour"),
        blank=True, null=True,
        help_text=_("Notes on condition or behaviour."), )

    habitat = models.CharField(
        max_length=500,
        verbose_name=_("Habitat"),
        choices=HABITAT_CHOICES,
        default=NA_VALUE,
        help_text=_("The habitat in which the animal was encountered."), )

    nesting_event = models.CharField(
        max_length=300,
        verbose_name=_("Nesting event"),
        choices=OBSERVATION_CHOICES,
        default=NA_VALUE,
        help_text=_("Was the animal nesting?"),)

    laparoscopy = models.BooleanField(
        max_length=300,
        verbose_name=_("Laparoscopy conducted"),
        default=False,
        help_text=_("Was the animal's sex and maturity determined through "
                    "laparoscopy?"),)

    checked_for_injuries = models.CharField(
        max_length=300,
        verbose_name=_("Checked for injuries"),
        choices=OBSERVATION_CHOICES,
        default=NA_VALUE,
        help_text=_("Was the animal checked for injuries, were any found?"),)

    scanned_for_pit_tags = models.CharField(
        max_length=300,
        verbose_name=_("Scanned for PIT tags"),
        choices=OBSERVATION_CHOICES,
        default=NA_VALUE,
        help_text=_("Was the animal scanned for PIT tags, were any found?"),)

    checked_for_flipper_tags = models.CharField(
        max_length=300,
        verbose_name=_("Checked for flipper tags"),
        choices=OBSERVATION_CHOICES,
        default=NA_VALUE,
        help_text=_("Was the animal checked for flipper tags, were any found?"),)

    cause_of_death = models.CharField(
        max_length=300,
        verbose_name=_("Cause of death"),
        choices=CAUSE_OF_DEATH_CHOICES,
        default=NA_VALUE,
        help_text=_("If dead, is the case of death known?"),)

    cause_of_death_confidence = models.CharField(
        max_length=300,
        verbose_name=_("Cause of death confidence"),
        choices=CONFIDENCE_CHOICES,
        default=NA_VALUE,
        help_text=_("What is the cause of death, if known, based on?"),)

    class Meta:
        """Class options."""

        ordering = ["when", "where"]
        verbose_name = "Animal Encounter"
        verbose_name_plural = "Animal Encounters"
        get_latest_by = "when"
        # base_manager_name = 'base_objects'  # fix delete bug

    def __str__(self):
        """The unicode representation."""
        tpl = "AnimalEncounter {0} on {1} by {2} of {3}, {4} {5} {6} on {7}"
        return tpl.format(
            self.pk,
            self.when.astimezone(tz.tzlocal()).strftime("%Y-%m-%d %H:%M %Z"),
            self.observer.name,
            self.get_species_display(),
            self.get_health_display(),
            self.get_maturity_display(),
            self.get_sex_display(),
            self.get_habitat_display())

    @property
    def get_encounter_type(self):
        """Infer the encounter type.

        AnimalEncounters are either in water, tagging or stranding encounters.
        If the animal is dead (at various decompositional stages), a stranding
        is assumed.
        In water captures happen if the habitat is in the list of aquatic
        habitats.
        Remaining encounters are assumed to be taggings, as other encounters are
        excluded. Note that an animal encountered in water, or even a dead
        animal (whether that makes sense or not) can also be tagged.
        """
        if self.nesting_event == "present":
            return Encounter.ENCOUNTER_TAGGING
        elif self.health in DEATH_STAGES:
            return Encounter.ENCOUNTER_STRANDING
        elif self.habitat in HABITAT_WATER:
            # this will ignore inwater encounters without habitat
            return Encounter.ENCOUNTER_INWATER
        else:
            # not stranding or in water = fallback to tagging
            return Encounter.ENCOUNTER_TAGGING

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
            self.when.astimezone(tz.tzlocal()).strftime("%Y-%m-%d %H:%M %Z"),
            force_text(round(self.longitude, 4)).replace(".", "-"),
            force_text(round(self.latitude, 4)).replace(".", "-"),
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

    The observations are assumed to follow DPaW protocol.
    TurtleNestEncouters by third parties can be recorded, but related
    observations cannot if they don't follow DPaW protocol.

    Stages:

    * false crawl (aborted nesting attempt)
    * new (turtle is present, observed during nesting/tagging)
    * fresh (morning after, observed during track count)
    * predated (nest and eggs destroyed by predator)
    * hatched (eggs hatched)
    """

    nest_age = models.CharField(
        max_length=300,
        verbose_name=_("Age"),
        choices=NEST_AGE_CHOICES,
        default=NEST_AGE_DEFAULT,
        help_text=_("The track or nest age."), )

    nest_type = models.CharField(
        max_length=300,
        verbose_name=_("Type"),
        choices=NEST_TYPE_CHOICES,
        default=NEST_TYPE_DEFAULT,
        help_text=_("The track or nest type."), )

    species = models.CharField(
        max_length=300,
        verbose_name=_("Species"),
        choices=TURTLE_SPECIES_CHOICES,
        default=TURTLE_SPECIES_DEFAULT,
        help_text=_("The species of the animal which created the track or nest."), )

    habitat = models.CharField(
        max_length=500,
        verbose_name=_("Habitat"),
        choices=BEACH_POSITION_CHOICES,
        default=NA_VALUE,
        help_text=_("The habitat in which the track or nest was encountered."), )

    disturbance = models.CharField(
        max_length=300,
        verbose_name=_("Evidence of predation or disturbance"),
        choices=OBSERVATION_CHOICES,
        default=NA_VALUE,
        help_text=_("Is there evidence of predation or other disturbance?"),)
    #
    # comments = models.TextField(
    #     verbose_name=_("Comments"),
    #     blank=True, null=True,
    #     help_text=_("Comments"), )

    class Meta:
        """Class options."""

        ordering = ["when", "where"]
        verbose_name = "Turtle Nest Encounter"
        verbose_name_plural = "Turtle Nest Encounters"
        get_latest_by = "when"
        # base_manager_name = 'base_objects'  # fix delete bug

    def __str__(self):
        """The unicode representation."""
        return "{0} {1} of {2} in {3}".format(
            self.get_nest_age_display(),
            self.get_nest_type_display(),
            self.get_species_display(),
            self.get_habitat_display(), )

    @property
    def get_encounter_type(self):
        """Infer the encounter type.

        TurtleNestEncounters are always nest encounters. Would you have guessed?
        """
        return Encounter.ENCOUNTER_NEST

    @property
    def short_name(self):
        """A short, often unique, human-readable representation of the encounter.

        Slugified and dash-separated:

        * Date of encounter as YYYY-mm-dd
        * longitude in WGS 84 DD, rounded to 4 decimals (<10m),
        * latitude in WGS 84 DD, rounded to 4 decimals (<10m), (missing sign!!)
        * nest age (type),
        * species,
        * name if available (requires "update names" and tag obs)

        The short_name could be non-unique.
        """
        nameparts = [
            self.when.astimezone(tz.tzlocal()).strftime("%Y-%m-%d %H:%M %Z"),
            force_text(round(self.longitude, 4)).replace(".", "-"),
            force_text(round(self.latitude, 4)).replace(".", "-"),
            self.nest_age,
            self.species,
        ]
        if self.name is not None:
            nameparts.append(self.name)
        return slugify.slugify("-".join(nameparts))


@python_2_unicode_compatible
class LineTransectEncounter(Encounter):
    """Encounter with a line transect.

    An observer tallies (not individually georeferenced) observations along
    a line transect, while recording the transect route live and keeping the
    tally until the end of the transect.

    Although individually geo-referenced Encounters are preferable, this Encounter
    type supports tallies of abundant entities (like turtle tracks on a saturation
    beach), collected under time pressure.

    Examples:

    ODK form "Track Tally", providing per record:
    * One LineTransectEncounter with zero to many related:
    * TrackTallyObservation
    * TurtleNestDisturbanceTallyObservation
    """

    transect = geo_models.LineStringField(
        srid=4326,
        verbose_name=_("Transect line"),
        help_text=_("The line transect as LineString in WGS84"))

    class Meta:
        """Class options."""

        ordering = ["when", "where"]
        verbose_name = "Line Transect Encounter"
        verbose_name_plural = "Line Transect Encounters"
        get_latest_by = "when"
        # base_manager_name = 'base_objects'  # fix delete bug

    def __str__(self):
        """The unicode representation."""
        return "Line tx {0}".format(
            self.pk
        )

    @property
    def get_encounter_type(self):
        """Infer the encounter type.

        If TrackTallyObservations are related, it's a track observation.

        TODO support other types of line transects when added
        """
        return Encounter.ENCOUNTER_NEST

    @property
    def short_name(self):
        """A short, often unique, human-readable representation of the encounter.

        Slugified and dash-separated:

        * Date of encounter as YYYY-mm-dd
        * longitude in WGS 84 DD, rounded to 4 decimals (<10m),
        * latitude in WGS 84 DD, rounded to 4 decimals (<10m), (missing sign!!)
        * nest age (type),
        * species,
        * name if available (requires "update names" and tag obs)

        The short_name could be non-unique.
        """
        nameparts = [
            self.when.astimezone(tz.tzlocal()).strftime("%Y-%m-%d %H:%M %Z"),
            force_text(round(self.longitude, 4)).replace(".", "-"),
            force_text(round(self.latitude, 4)).replace(".", "-")
        ]
        if self.name is not None:
            nameparts.append(self.name)
        return slugify.slugify("-".join(nameparts))


@python_2_unicode_compatible
class LoggerEncounter(Encounter):
    """The encounter of an electronic logger during its life cycle.

    Stages:

    * programmed (in office)
    * posted to field team (in mail)
    * deployed (in situ)
    * resighted (in situ)
    * retrieved (in situ)
    * downloaded (in office)

    The life cycle can be repeated. The logger can be downloaded, reprogrammed
    and deployed again in situ.
    """

    LOGGER_TYPE_DEFAULT = 'temperature-logger'
    LOGGER_TYPE_CHOICES = (
        (LOGGER_TYPE_DEFAULT, 'Temperature Logger'),
        ('data-logger', 'Data Logger'),
        ('ctd-data-logger', 'Conductivity, Temperature, Depth SR data logger'),
    )

    LOGGER_STATUS_DEFAULT = 'resighted'
    LOGGER_STATUS_NEW = "programmed"
    LOGGER_STATUS_CHOICES = (
        (LOGGER_STATUS_NEW, "programmed"),
        ("posted", "posted to field team"),
        ("deployed", "deployed in situ"),
        ("resighted", "resighted in situ"),
        ("retrieved", "retrieved in situ"),
        ("downloaded", "downloaded"),
    )

    logger_type = models.CharField(
        max_length=300,
        default=LOGGER_TYPE_DEFAULT,
        verbose_name=_("Type"),
        choices=LOGGER_TYPE_CHOICES,
        help_text=_("The logger type."), )

    deployment_status = models.CharField(
        max_length=300,
        default=LOGGER_STATUS_DEFAULT,
        verbose_name=_("Status"),
        choices=LOGGER_STATUS_CHOICES,
        help_text=_("The logger life cycle status."), )

    logger_id = models.CharField(
        max_length=1000,
        blank=True, null=True,
        verbose_name=_("Logger ID"),
        help_text=_("The ID of a logger must be unique within the tag type."),)

    # comments = models.TextField(
    #     verbose_name=_("Comment"),
    #     blank=True, null=True,
    #     help_text=_("Comments"), )

    class Meta:
        """Class options."""

        ordering = ["when", "where"]
        verbose_name = "Logger Encounter"
        verbose_name_plural = "Logger Encounters"
        get_latest_by = "when"
        # base_manager_name = 'base_objects'  # fix delete bug

    def __str__(self):
        """The unicode representation."""
        return "{0} {1} {2}".format(
            self.get_logger_type_display(),
            self.name or '',
            self.get_deployment_status_display(),
        )

    @property
    def get_encounter_type(self):
        """Infer the encounter type.

        LoggerEncounters are always logger encounters. Would you have guessed?
        """
        return Encounter.ENCOUNTER_LOGGER

    @property
    def short_name(self):
        """A short, often unique, human-readable representation of the encounter.

        Slugified and dash-separated:

        * logger type
        * deployment status
        * logger id

        The short_name could be non-unique for very similar encounters.
        In this case, a modifier can be added by the user to ensure uniqueness.
        """
        nameparts = [
            self.logger_type,
            self.deployment_status,
            self.logger_id
        ]
        if self.name is not None:
            nameparts.append(self.name)
        return slugify.slugify("-".join(nameparts))

    @property
    def inferred_name(self):
        """Set the encounter name from logger ID."""
        return self.logger_id


# Observation models ---------------------------------------------------------#
@python_2_unicode_compatible
class Observation(PolymorphicModel, models.Model):
    """The Observation base class for encounter observations.

    Everything happens somewhere, at a time, to someone, and someone records it.
    Therefore, an Observation must happen during an Encounter.
    """

    encounter = models.ForeignKey(
        Encounter,
        on_delete=models.CASCADE,
        verbose_name=_("Encounter"),
        help_text=("The Encounter during which the observation was made"),)

    class Meta:
        """Class options."""

        # base_manager_name = 'base_objects'

    def __str__(self):
        """The unicode representation."""
        return u"Obs {0} for {1}".format(self.pk, self.encounter.__str__())

    @property
    def point(self):
        """Return the encounter location."""
        return self.encounter.where

    @property
    def as_html(self):
        """An HTML representation."""
        t = loader.get_template("popup/{0}.html".format(self._meta.model_name))
        # c = Context({"original": self})
        return mark_safe(t.render({"original": self}))

    @property
    def as_latex(self):
        """A Latex representation."""
        t = loader.get_template("latex/{0}.tex".format(self._meta.model_name))
        # c = Context({"original": self})
        return mark_safe(t.render({"original": self}))

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
        return self.encounter.where.y or ''

    @property
    def longitude(self):
        """The encounter's longitude."""
        return self.encounter.where.x or ''

    def datetime(self):
        """The encounter's timestamp."""
        return self.encounter.when or ''


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

    class Meta:
        """Class options."""

        # base_manager_name = 'base_objects'

    def __str__(self):
        """The unicode representation."""
        return u"Media {0} for {1}".format(self.pk, self.encounter.__str__())

    @property
    def filepath(self):
        """The path to attached file."""
        try:
            fpath = force_text(self.attachment.file)
        except:
            fpath = None
        return fpath


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

    As TagObservations can sometimes occur without an Observation of an animal,
    the FK to Observations is optional.

    Flipper Tag Status as per WAMTRAM:

    * # = tag attached new, number NA, need to double-check number
    * P, p: re-sighted as attached to animal, no actions taken or necessary
    * do not use: 0L, A2, M, M1, N
    * AE = A1
    * P_ED = near flipper edge, might fall off soon
    * PX = tag re-sighted, but operator could not read tag ID
      (e.g. turtle running off)
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
        on_delete=models.PROTECT,
        blank=True, null=True,
        verbose_name=_("Handled by"),
        related_name="tag_handler",
        help_text=_("The person in physical contact with the tag or sample"))

    recorder = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
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
        return u"{0} {1} {2} on {3}".format(
            self.get_tag_type_display(),
            self.name,
            self.get_status_display(),
            self.get_tag_location_display())

    @classmethod
    def encounter_history(cls, tagname):
        """Return the related encounters of all TagObservations of a given tag name."""
        return list(set([t.encounter for t in cls.objects.filter(name=tagname)]))

    @classmethod
    def encounter_histories(cls, tagname_list, without=[]):
        """Return the related encounters of all tag names.

        TODO double-check performance
        """
        return [encounter
                for encounter
                in list(set(itertools.chain.from_iterable(
                    [TagObservation.encounter_history(t.name) for t in tagname_list])))
                if encounter not in without]

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
        return "{0}?q={1}".format(cl, urllib.parse.quote_plus(self.name))


@python_2_unicode_compatible
class NestTagObservation(Observation):
    """Turtle Nest Tag Observation.

    TNTs consist of three components, which are all optional:

    * flipper_tag_id: The primary flipper tag ID of the nesting turtle
    * date_nest_laid: The calendar (not turtle) date of nest creation
    * tag_label: Any extra nest label if other two components not available

    Naming scheme:

    * Uppercase and remove whitespace from flipper tag ID
    * date nest laid: YYYY-mm-dd
    * Uppercase and remove whitespace from tag label
    * Join all with "_"

    E.g.: WA1234_2017-12-31_M1
    """

    status = models.CharField(
        max_length=300,
        verbose_name=_("Tag status"),
        choices=NEST_TAG_STATUS_CHOICES,
        default=TAG_STATUS_DEFAULT,
        help_text=_("The status this tag was seen in, or brought into."),)

    flipper_tag_id = models.CharField(
        max_length=1000,
        blank=True, null=True,
        verbose_name=_("Flipper Tag ID"),
        help_text=_("The primary flipper tag ID of the nesting turtle "
                    "if available."),)

    date_nest_laid = models.DateField(
        verbose_name=_("Date nest laid"),
        blank=True, null=True,
        help_text=_("The calendar (not turtle) date of nest creation."))

    tag_label = models.CharField(
        max_length=1000,
        blank=True, null=True,
        verbose_name=_("Tag Label"),
        help_text=_("Any extra nest label if other two components are not "
                    "available."),)

    comments = models.TextField(
        verbose_name=_("Comments"),
        blank=True, null=True,
        help_text=_("Any other comments or notes."),)

    def __str__(self):
        """The unicode representation."""
        return u"{0} ({1})".format(self.name, self.get_status_display())

    # def save(self, *args, **kwargs):
    #     """Cache name, centroid and northern extent."""
    #     super(NestTagObservation, self).save(*args, **kwargs)

    @property
    def history_url(self):
        """The list view of all observations of this tag."""
        cl = reverse("admin:observations_nesttagobservation_changelist")
        if self.flipper_tag_id:
            return "{0}?q={1}".format(cl, urllib.parse.quote_plus(self.flipper_tag_id))
        else:
            return cl

    @property
    def name(self):
        """Return the nest tag name according to the naming scheme."""
        return "_".join([
            ('' if not self.flipper_tag_id else self.flipper_tag_id).upper().replace(" ", ""),
            '' if not self.date_nest_laid else self.date_nest_laid.strftime("%Y-%m-%d"),
            '' if not self.tag_label else self.tag_label.upper().replace(" ", ""),
        ])


@receiver(pre_save, sender=NestTagObservation)
def nesttagobservation_pre_save(sender, instance, *args, **kwargs):
    """NestTagObservation pre_save: sanitise tag_label, name Encounter after tag."""
    if instance.encounter.status == Encounter.STATUS_NEW and instance.tag_label:
        instance.tag_label = sanitize_tag_label(instance.tag_label)
    if instance.encounter.status == Encounter.STATUS_NEW and instance.flipper_tag_id:
        instance.flipper_tag_id = sanitize_tag_label(instance.flipper_tag_id)
    if instance.encounter.status == Encounter.STATUS_NEW and (not instance.encounter.name):
        instance.encounter.name = instance.name
        instance.encounter.save(update_fields=['name', ])


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
        return u"Management Action {0} of {1}".format(
            self.pk, self.encounter.__str__())


@python_2_unicode_compatible
class TurtleMorphometricObservation(Observation):
    """Morphometric measurements of a turtle."""

    curved_carapace_length_mm = models.PositiveIntegerField(
        verbose_name=_("Curved carapace length (mm)"),
        blank=True, null=True,
        help_text=_("The curved carapace length in millimetres."),)

    curved_carapace_length_accuracy = models.CharField(
        max_length=300,
        blank=True, null=True,
        choices=ACCURACY_CHOICES,
        verbose_name=_("Curved carapace length accuracy"),
        help_text=_("The expected measurement accuracy."),)

    straight_carapace_length_mm = models.PositiveIntegerField(
        blank=True, null=True,
        verbose_name=_("Straight carapace length (mm)"),
        help_text=_("The straight carapace length in millimetres."),)

    straight_carapace_length_accuracy = models.CharField(
        max_length=300,
        blank=True, null=True,
        choices=ACCURACY_CHOICES,
        verbose_name=_("Straight carapace length accuracy"),
        help_text=_("The expected measurement accuracy."),)

    curved_carapace_width_mm = models.PositiveIntegerField(
        blank=True, null=True,
        verbose_name=_("Curved carapace width (mm)"),
        help_text=_("Curved carapace width in millimetres."),)

    curved_carapace_width_accuracy = models.CharField(
        max_length=300,
        blank=True, null=True,
        choices=ACCURACY_CHOICES,
        verbose_name=_("Curved carapace width (mm)"),
        help_text=_("The expected measurement accuracy."),)

    tail_length_carapace_mm = models.PositiveIntegerField(
        blank=True, null=True,
        verbose_name=_("Tail length from carapace (mm)"),
        help_text=_("The tail length in millimetres, "
                    "measured from carapace to tip."),)

    tail_length_carapace_accuracy = models.CharField(
        max_length=300,
        blank=True, null=True,
        choices=ACCURACY_CHOICES,
        verbose_name=_("Tail length from carapace accuracy"),
        help_text=_("The expected measurement accuracy."),)

    tail_length_vent_mm = models.PositiveIntegerField(
        blank=True, null=True,
        verbose_name=_("Tail length from vent (mm)"),
        help_text=_("The tail length in millimetres, "
                    "measured from vent to tip."),)

    tail_length_vent_accuracy = models.CharField(
        max_length=300,
        blank=True, null=True,
        choices=ACCURACY_CHOICES,
        verbose_name=_("Tail Length Accuracy"),
        help_text=_("The expected measurement accuracy."),)

    tail_length_plastron_mm = models.PositiveIntegerField(
        blank=True, null=True,
        verbose_name=_("Tail length from plastron (mm)"),
        help_text=_("The tail length in millimetres, "
                    "measured from plastron to tip."),)

    tail_length_plastron_accuracy = models.CharField(
        max_length=300,
        blank=True, null=True,
        choices=ACCURACY_CHOICES,
        verbose_name=_("Tail length from plastron accuracy"),
        help_text=_("The expected measurement accuracy."),)

    maximum_head_width_mm = models.PositiveIntegerField(
        blank=True, null=True,
        verbose_name=_("Maximum head width (mm)"),
        help_text=_("The maximum head width in millimetres."),)

    maximum_head_width_accuracy = models.CharField(
        max_length=300,
        blank=True, null=True,
        choices=ACCURACY_CHOICES,
        verbose_name=_("Maximum head width accuracy"),
        help_text=_("The expected measurement accuracy."),)

    maximum_head_length_mm = models.PositiveIntegerField(
        blank=True, null=True,
        verbose_name=_("Maximum head length (mm)"),
        help_text=_("The maximum head length in millimetres."),)

    maximum_head_length_accuracy = models.CharField(
        max_length=300,
        blank=True, null=True,
        choices=ACCURACY_CHOICES,
        verbose_name=_("Maximum head length accuracy"),
        help_text=_("The expected measurement accuracy."),)

    body_depth_mm = models.PositiveIntegerField(
        blank=True, null=True,
        verbose_name=_("Body depth (mm)"),
        help_text=_("The body depth, plastron to carapace, in millimetres."),)

    body_depth_accuracy = models.CharField(
        max_length=300,
        blank=True, null=True,
        choices=ACCURACY_CHOICES,
        verbose_name=_("Body depth accuracy"),
        help_text=_("The expected measurement accuracy."),)

    body_weight_g = models.PositiveIntegerField(
        blank=True, null=True,
        verbose_name=_("Body weight (g)"),
        help_text=_("The body weight in grams (1000 g = 1kg)."),)

    body_weight_accuracy = models.CharField(
        max_length=300,
        blank=True, null=True,
        choices=ACCURACY_CHOICES,
        verbose_name=_("Body weight accuracy"),
        help_text=_("The expected measurement accuracy."),)

    handler = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        blank=True, null=True,
        related_name="morphometric_handler",
        verbose_name=_("Measured by"),
        help_text=_("The person conducting the measurements."))

    recorder = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        blank=True, null=True,
        related_name="morphometric_recorder",
        verbose_name=_("Recorded by"),
        help_text=_("The person recording the measurements."))

    def __str__(self):
        """The unicode representation."""
        tpl = u"Turtle Morphometrics {0} CCL {1} CCW {2} for Encounter {3}"
        return tpl.format(
            self.pk,
            self.curved_carapace_length_mm,
            self.curved_carapace_width_mm,
            self.encounter.pk)


@python_2_unicode_compatible
class HatchlingMorphometricObservation(Observation):
    """Morphometric measurements of a hatchling at a TurtleNestEncounter."""

    straight_carapace_length_mm = models.PositiveIntegerField(
        blank=True, null=True,
        verbose_name=_("Straight carapace length (mm)"),
        help_text=_("The straight carapace length in millimetres."),)

    straight_carapace_width_mm = models.PositiveIntegerField(
        blank=True, null=True,
        verbose_name=_("Straight carapace width (mm)"),
        help_text=_("The straight carapace width in millimetres."),)

    body_weight_g = models.PositiveIntegerField(
        blank=True, null=True,
        verbose_name=_("Body weight (g)"),
        help_text=_("The body weight in grams (1000 g = 1kg)."),)

    def __str__(self):
        """The unicode representation."""
        tpl = u"{0} {1} Hatchling SCL {2} mm, SCW {3} mm, Wt {4} g"
        return tpl.format(
            self.pk,
            self.encounter.species,
            self.straight_carapace_length_mm,
            self.straight_carapace_width_mm,
            self.body_weight_g,
        )


@python_2_unicode_compatible
class DugongMorphometricObservation(Observation):
    """Morphometric measurements of a Dugong at an AnimalEncounter."""

    body_length_mm = models.PositiveIntegerField(
        blank=True, null=True,
        verbose_name=_("Body length (mm)"),
        help_text=_("The body length in millimetres."),)

    body_girth_mm = models.PositiveIntegerField(
        blank=True, null=True,
        verbose_name=_("Body girth (mm)"),
        help_text=_("The body girth at the widest point in millimetres."),)

    tail_fluke_width_mm = models.PositiveIntegerField(
        blank=True, null=True,
        verbose_name=_("Tail fluke width (mm)"),
        help_text=_("The tail fluke width in millimetres."),)

    tusks_found = models.CharField(
        max_length=300,
        verbose_name=_("Tusks found"),
        choices=OBSERVATION_CHOICES,
        default=NA_VALUE,
        help_text=_("Did the animal have tusks?"), )

    def __str__(self):
        """The unicode representation."""
        tpl = u"{0} {1} Hatchling SCL {2} mm, SCW {3} mm, Wt {4} g"
        return tpl.format(
            self.pk,
            self.encounter.species,
            self.body_length_mm,
            self.body_girth_mm,
            self.tail_fluke_width_mm,
        )


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
        return u"{0}: {1} {2}".format(
            self.get_body_part_display(),
            self.get_damage_age_display(),
            self.get_damage_type_display(), )


@python_2_unicode_compatible
class TrackTallyObservation(Observation):
    """Observation of turtle track tallies and signs of predation."""

    species = models.CharField(
        max_length=300,
        verbose_name=_("Species"),
        choices=TURTLE_SPECIES_CHOICES,
        default=TURTLE_SPECIES_DEFAULT,
        help_text=_("The species of the animal causing the track."), )

    nest_age = models.CharField(
        max_length=300,
        verbose_name=_("Age"),
        choices=NEST_AGE_CHOICES,
        default=NEST_AGE_DEFAULT,
        help_text=_("The track or nest age."), )

    nest_type = models.CharField(
        max_length=300,
        verbose_name=_("Type"),
        choices=NEST_TYPE_CHOICES,
        default=NEST_TYPE_DEFAULT,
        help_text=_("The track or nest type."), )

    tally = models.PositiveIntegerField(
        verbose_name=_("Tally"),
        blank=True, null=True,
        help_text=_("The sum of encountered tracks."),)

    def __str__(self):
        """The unicode representation."""
        t1 = (u'TrackTally: {0} {1} {2}s of {3}')
        return t1.format(self.tally, self.nest_age, self.nest_type, self.species)


@python_2_unicode_compatible
class TurtleNestDisturbanceTallyObservation(Observation):
    """Observation of turtle track tallies and signs of predation."""

    species = models.CharField(
        max_length=300,
        verbose_name=_("Species"),
        choices=TURTLE_SPECIES_CHOICES,
        default=TURTLE_SPECIES_DEFAULT,
        help_text=_("The species of the nesting animal."), )

    disturbance_cause = models.CharField(
        max_length=300,
        verbose_name=_("Disturbance cause"),
        choices=NEST_DAMAGE_CHOICES,
        default=NEST_DAMAGE_DEFAULT,
        help_text=_("The cause of the disturbance."), )

    no_nests_disturbed = models.PositiveIntegerField(
        verbose_name=_("Tally of nests disturbed"),
        blank=True, null=True,
        help_text=_("The sum of damaged nests."),)

    no_tracks_encountered = models.PositiveIntegerField(
        verbose_name=_("Tally of disturbance signs"),
        blank=True, null=True,
        help_text=_("The sum of signs, e.g. predator tracks."),)

    comments = models.TextField(
        verbose_name=_("Comments"),
        blank=True, null=True,
        help_text=_("Any other comments or notes."),)

    def __str__(self):
        """The unicode representation."""
        t1 = ('Nest Damage Tally: {0} nests of {1} showing disturbance by {2} '
              '({3} disturbance signs sighted)')
        return t1.format(self.no_nests_disturbed, self.species,
                         self.disturbance_cause, self.no_tracks_encountered)


@python_2_unicode_compatible
class TurtleNestObservation(Observation):
    """Turtle nest observations.

    This model supports data sheets for:

    * Turtle nest observation during tagging
    * Turtle nest excavation a few days after hatching

    Egg count is done as total, plus categories of nest contents following
    "Determining Clutch Size and Hatching Success, Jeffrey D. Miller,
    Research and Management Techniques for the Conservation of Sea Turtles,
    IUCN Marine Turtle Specialist Group, 1999.
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
        help_text=_("The total number of eggs laid as observed during tagging."), )

    # start Miller fields
    # no_emerged = models.PositiveIntegerField(
    #     verbose_name=_("Emerged (E)"),
    #     blank=True, null=True,
    #     help_text=_("The number of hatchlings leaving or departed from nest."
    #                 "Calculated from S - (L + D)."), )

    no_egg_shells = models.PositiveIntegerField(
        verbose_name=_("Egg shells (S)"),
        blank=True, null=True,
        help_text=_("The number of empty shells counted which were "
                    "more than 50 percent complete."), )

    no_live_hatchlings_neck_of_nest = models.PositiveIntegerField(
        verbose_name=_("Live hatchlings in neck of nest"),
        blank=True, null=True,
        help_text=_("The number of live hatchlings in the neck of the nest."),)

    no_live_hatchlings = models.PositiveIntegerField(
        verbose_name=_("Live hatchlings in nest (L)"),
        blank=True, null=True,
        help_text=_("The number of live hatchlings left among shells "
                    "excluding those in neck of nest."),)

    no_dead_hatchlings = models.PositiveIntegerField(
        verbose_name=_("Dead hatchlings (D)"),
        blank=True, null=True,
        help_text=_("The number of dead hatchlings that have left"
                    " their shells."),)

    no_undeveloped_eggs = models.PositiveIntegerField(
        verbose_name=_("Undeveloped eggs (UD)"),
        blank=True, null=True,
        help_text=_("The number of unhatched eggs with no obvious embryo."),)

    no_unhatched_eggs = models.PositiveIntegerField(
        verbose_name=_("Unhatched eggs (UH)"),
        blank=True, null=True,
        help_text=_("The number of unhatched eggs with obvious, "
                    "not yet full term, embryo."),)

    no_unhatched_term = models.PositiveIntegerField(
        verbose_name=_("Unhatched term (UHT)"),
        blank=True, null=True,
        help_text=_("The number of unhatched, apparently full term, embryo"
                    " in egg or pipped with small amount of external"
                    " yolk material."),)

    no_depredated_eggs = models.PositiveIntegerField(
        verbose_name=_("Depredated eggs (P)"),
        blank=True, null=True,
        help_text=_("The number of open, nearly complete shells containing "
                    "egg residue."),)

    # end Miller fields
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

    comments = models.TextField(
        verbose_name=_("Comments"),
        blank=True, null=True,
        help_text=_("Any other comments or notes."),)

    class Meta:
        """Class opts."""

        verbose_name = "Turtle Nest Excavation"

    def __str__(self):
        """The unicode representation."""
        return u"Nest Obs {0} eggs, hatching succ {1}, emerg succ {2}".format(
            self.egg_count, self.hatching_success, self.emergence_success)

    # TODO custom save()
    # calculate egg_count;

    @property
    def no_emerged(self):
        """The number of hatchlings leaving or departed from nest is S-(L+D)."""
        return (
            (self.no_egg_shells or 0) -
            (self.no_live_hatchlings or 0) -
            (self.no_dead_hatchlings or 0)
        )

    @property
    def egg_count_calculated(self):
        """The calculated egg count from nest excavations.

        Calculated as:

        no_egg_shells + no_undeveloped_eggs + no_unhatched_eggs +
        no_unhatched_term + no_depredated_eggs
        """
        return (
            (self.no_egg_shells or 0) +
            (self.no_undeveloped_eggs or 0) +
            (self.no_unhatched_eggs or 0) +
            (self.no_unhatched_term or 0) +
            (self.no_depredated_eggs or 0))

    @property
    def hatching_success(self):
        """Return the hatching success as percentage [0..100].

        Formula after Miller 1999::

            Hatching success = 100 * no_egg_shells / (
                no_egg_shells + no_undeveloped_eggs + no_unhatched_eggs +
                no_unhatched_term + no_depredated_eggs)
        """
        if (self.egg_count_calculated == 0):
            return 0
        else:
            return round(100 * (self.no_egg_shells or 0) / self.egg_count_calculated, 2)

    @property
    def emergence_success(self):
        """Return the emergence success as percentage [0..100].

        Formula after Miller 1999::

            Emergence success = 100 *
                (no_egg_shells - no_live_hatchlings - no_dead_hatchlings) / (
                no_egg_shells + no_undeveloped_eggs + no_unhatched_eggs +
                no_unhatched_term + no_depredated_eggs)
        """
        if (self.egg_count_calculated == 0):
            return 0
        else:
            return round(100 * (
                (self.no_egg_shells or 0) -
                (self.no_live_hatchlings or 0) -
                (self.no_dead_hatchlings or 0)
            ) / self.egg_count_calculated, 2)


@python_2_unicode_compatible
class TurtleNestDisturbanceObservation(Observation):
    """Turtle nest disturbance observations.

    Disturbance can be a result of:

    * Predation
    * Disturbance by other turtles
    * Environmental disturbance (cyclones, tides)
    * Anthropogenic disturbance (vehicle damage, poaching, research, harvest)
    """

    NEST_VIABILITY_CHOICES = (
        ("partly", "nest partly destroyed"),
        ("completely", "nest completely destroyed"),
        (NA_VALUE, "nest in indeterminate condition"),
    )

    disturbance_cause = models.CharField(
        max_length=300,
        verbose_name=_("Disturbance cause"),
        choices=NEST_DAMAGE_CHOICES,
        help_text=_("The cause of the disturbance."), )

    disturbance_cause_confidence = models.CharField(
        max_length=300,
        verbose_name=_("Disturbance cause choice confidence"),
        choices=CONFIDENCE_CHOICES,
        default=NA_VALUE,
        help_text=_("What is the choice of disturbance cause based on?"),)

    disturbance_severity = models.CharField(
        max_length=300,
        verbose_name=_("Disturbance severity"),
        choices=NEST_VIABILITY_CHOICES,
        default=NA_VALUE,
        help_text=_("The impact of the disturbance on nest viability."), )

    comments = models.TextField(
        verbose_name=_("Comments"),
        blank=True, null=True,
        help_text=_("Any other comments or notes."),)

    def __str__(self):
        """The unicode representation."""
        return u"Nest Disturbance {0} {1}".format(
            self.disturbance_cause, self.disturbance_severity)


# @python_2_unicode_compatible
# class TurtleHatchlingEmergenceObservation(Observation):
    """Turtle hatchling emergence observation.

    Hatchling emergence observations can include:

    * Emergence time (if seen directly),
    * Fan angles of hatchling tracks forming a fan from nest to sea,
    * Emergence climate
    * Outliers present (if yes: TurtleHatchlingEmergenceOutlierObservation)
    * Light sources known and present (if yes: LightSourceObservation).

    # TON 0.54+
    "fan_angles": {
        "photo_hatchling_tracks_seawards": "1546836969404.jpg",
        "photo_hatchling_tracks_relief": null,
        "bearing_to_water_manual": "98.0000000000",
        "leftmost_track_manual": "58.0000000000",
        "rightmost_track_manual": "122.0000000000",
        "no_tracks_main_group": "7",
        "no_tracks_main_group_min": "7",
        "no_tracks_main_group_max": "7",
        "outlier_tracks_present": "present",
        "hatchling_path_to_sea": "clear",
        "path_to_sea_comments": null,
        "hatchling_emergence_time_known": "yes",
        "cloud_cover_at_emergence_known": "yes",
        "light_sources_present": "present"
      },
      "outlier_track": {
        "outlier_track_photo": "1546837474680.jpg",
        "outlier_track_bearing_manual": "180.0000000000",
        "outlier_group_size": "1",
        "outlier_track_comment": null
      },
      "hatchling_emergence_time_group": {
        "hatchling_emergence_time": "2019-01-06T23:07:00.000Z",
        "hatchling_emergence_time_source": "plusminus-2h"
      },
      "emergence_climate": {
        "cloud_cover_at_emergence": "3"
      },
      "light_source": [
        {
          "light_source_photo": null,
          "light_bearing_manual": "50.0000000000",
          "light_source_type": "artificial",
          "light_source_description": "Oil rig#5"
        },
        {
          "light_source_photo": null,
          "light_bearing_manual": "190.0000000000",
          "light_source_type": "natural",
          "light_source_description": "Moon"
        }
      ],
      "other_light_sources": {
        "other_light_sources_present": "na"
      }
    """
    # pass

# LightSourceObservation
# TurtleHatchlingEmergenceOutlierObservation

# TODO add CecaceanMorphometricObservation for cetacean strandings

# Logger Observation models --------------------------------------------------#


@python_2_unicode_compatible
class TemperatureLoggerSettings(Observation):
    """Temperature Logger Settings."""

    logging_interval = DurationField(
        verbose_name=_("Logging interval"),
        blank=True, null=True,
        help_text=_("The time between individual readings as python timedelta "
                    "string. E.g, 1h is `01:00:00`; 1 day is `1 00:00:00`."), )

    recording_start = models.DateTimeField(
        verbose_name=_("Recording start"),
        blank=True, null=True,
        help_text=_("The preset start of recording, stored as UTC and "
                    "shown in local time."), )

    tested = models.CharField(
        max_length=300,
        verbose_name=_("Tested"),
        choices=OBSERVATION_CHOICES,
        default=NA_VALUE,
        help_text=_("Was the logger tested after programming?"), )

    def __str__(self):
        """The unicode representation."""
        return u"Sampling starting on {0} with rate {1}".format(
            self.recording_start, self.logging_interval)


@python_2_unicode_compatible
class DispatchRecord(Observation):
    """A record of dispatching the subject of the encounter."""

    sent_to = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name=_("Sent to"),
        related_name="receiver",
        blank=True, null=True,
        help_text=_("The receiver of the dispatch."), )

    # sent_on = models.DateField(
    #     verbose_name=_("Sent on"),
    #     blank=True, null=True,
    #     help_text=_("The date of dispatch."))

    def __str__(self):
        """The unicode representation."""
        return u"Sent on {0} to {1}".format(self.encounter.when, self.sent_to)


@python_2_unicode_compatible
class TemperatureLoggerDeployment(Observation):
    """A record of deploying a temperature logger."""

    depth_mm = models.PositiveIntegerField(
        verbose_name=_("Logger depth (mm)"),
        blank=True, null=True,
        help_text=_("The depth of the buried logger in mm."),)

    marker1_present = models.CharField(
        max_length=300,
        verbose_name=_("Marker 1 present"),
        choices=OBSERVATION_CHOICES,
        default=NA_VALUE,
        help_text=_("Is the first marker in place?"),)

    distance_to_marker1_mm = models.PositiveIntegerField(
        verbose_name=_("Distance to marker 1 (mm)"),
        blank=True, null=True,
        help_text=_("The distance to the first marker in mm."),)

    marker2_present = models.CharField(
        max_length=300,
        verbose_name=_("Marker 2 present"),
        choices=OBSERVATION_CHOICES,
        default=NA_VALUE,
        help_text=_("Is the second marker in place?"),)

    distance_to_marker2_mm = models.PositiveIntegerField(
        verbose_name=_("Distance to marker 2 (mm)"),
        blank=True, null=True,
        help_text=_("The distance to the second marker in mm."),)

    habitat = models.CharField(
        max_length=500,
        verbose_name=_("Habitat"),
        choices=HABITAT_CHOICES,
        default="na",
        help_text=_("The habitat in which the nest was encountered."), )

    distance_to_vegetation_mm = models.PositiveIntegerField(
        verbose_name=_("Distance to vegetation (mm)"),
        blank=True, null=True,
        help_text=_("The distance to the beach-vegetation border in mm. "
                    "Positive values if logger is located on beach, "
                    "negative values if in vegetation."),)

    def __str__(self):
        """The unicode representation."""
        return u"Logger at {0} mm depth".format(self.depth_mm)
