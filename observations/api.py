from django_filters.rest_framework import DateFilter
from rest_framework.viewsets import ModelViewSet
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework_filters import FilterSet
from shared.api import (
    MyGeoJsonPagination,
    BatchUpsertViewSet,
    ObservationBatchUpsertViewSet
)
from observations import models, serializers
try:
    from .utils import symlink_resources
except BaseException:
    # Docker image build migrate falls over this import
    pass


class AreaFilter(FilterSet):

    class Meta:
        model = models.Area
        fields = {
            "area_type": ["exact", "in", "startswith"],
            "name": ["exact", "iexact", "in", "startswith", "contains", "icontains"],
        }


class AreaViewSet(ModelViewSet):
    """Area viewset.

    # Filters

    # name
    * [/api/1/areas/?name__startswith=Broome](/api/1/areas/?name__startswith=Broome)
      Areas starting with "Broome"
    * [/api/1/areas/?name__icontains=sector](/api/1/areas/?name__icontains=Sector)
      Areas containing (case-insensitive) "sector"
    * [/api/1/areas/?name=Cable Beach Broome Sector 3](/api/1/areas/?name=Cable Beach Broome Sector 3)
      Area with exact name (case sensitive)


    # area_type
    * [/api/1/areas/?area_type=MPA](/api/1/areas/?area_type=MPA) Marine Protected Areas
    * [/api/1/areas/?area_type=Locality](/api/1/areas/?area_type=Locality)
      Localities (typically containing multiple surveyed sites)
    * [/api/1/areas/?area_type=Site](/api/1/areas/?area_type=Site) Sites (where Surveys are conducted)
    """
    queryset = models.Area.objects.all()
    serializer_class = serializers.AreaSerializer
    filter_class = AreaFilter
    bbox_filter_field = "geom"
    pagination_class = MyGeoJsonPagination


class CampaignViewSet(BatchUpsertViewSet):
    """Campaign ModelViewSet.

    alt: BatchUpsertViewSet

    All filters are available on all fields except location and team.
    """
    queryset = models.Campaign.objects.all().prefetch_related("owner", "viewers")
    serializer_class = serializers.CampaignSerializer
    # filter_class = CampaignFilter
    pagination_class = MyGeoJsonPagination  # provides top level features
    model = models.Campaign


class SurveyFilter(FilterSet):
    """Survey Filter. All filter methods available on all fields except location and team.

    # Dates
    * [/api/1/surveys/?start_time__year__in=2017,2018](/api/1/surveys/?start_time__year__in=2017,2018) Years 2017, 2018
    """
    start_time = DateFilter()
    end_time = DateFilter()

    class Meta:
        model = models.Survey
        fields = {
            "id": "__all__",
            "area": "__all__",
            "site": "__all__",
            "start_time": "__all__",
            "end_time": "__all__",
            "start_comments": "__all__",
            "end_comments": "__all__",
            "reporter": "__all__",
            "device_id": "__all__",
            "end_device_id": "__all__",
            "source_id": "__all__",
            "end_source_id": "__all__",
            "status": "__all__",
            "production": "__all__",
        }


class SurveyViewSet(BatchUpsertViewSet):
    """Survey ModelViewSet.

    alt: BatchUpsertViewSet

    All filters are available on all fields except location and team.
    """
    queryset = models.Survey.objects.all().prefetch_related("reporter", "area", "site", "team")
    serializer_class = serializers.SurveySerializer
    filter_class = SurveyFilter
    pagination_class = MyGeoJsonPagination  # provides top level features
    model = models.Survey


class SurveyMediaAttachmentViewSet(ModelViewSet):
    """Binary media (photos, datasheet PDFs etc) of Surveys.

    Can be many per Survey.

    [Admin](/admin/observations/survey-media-attachments/)
    """
    queryset = models.SurveyMediaAttachment.objects.all().prefetch_related(
        "survey__reporter", "survey__site", "survey__area")
    serializer_class = serializers.SurveyMediaAttachmentSerializer
    pagination_class = MyGeoJsonPagination
    parser_classes = [FormParser, MultiPartParser]
    model = models.SurveyMediaAttachment


class EncounterFilter(FilterSet):
    when = DateFilter()

    class Meta:
        model = models.Encounter
        fields = {
            "source": ["iexact", "icontains"],
            "area": "__all__",
            "site": "__all__",
            "survey": "__all__",
            "location_accuracy": ["iexact", "icontains"],
            "when": ["iexact", "icontains"],
            "name": ["iexact", "icontains"],
            "source_id": ["iexact", "icontains"],
            "observer": "__all__",
            "reporter": "__all__",
            "comments": ["iexact", "icontains"],
        }


class FastEncounterFilter(FilterSet):
    when = DateFilter()

    class Meta:
        model = models.Encounter
        fields = {
            "source": ["iexact", "icontains"],
            "when": "__all__",
            "source_id": ["iexact", "icontains"],
        }


class EncounterViewSet(BatchUpsertViewSet):
    """Encounters are a common, minimal, shared set of data about:

    * Strandings (turtles, dugong, ceataceans (pre-QA raw import), pinnipeds (coming soon), sea snakes)
    * Turtle tagging (if and where imported as copy from WAMTRAM 2)
    * Turtle track counts (all)
    * Random encounters of animals

    # Filters
    Combine arguments with &, e.g.
    [/api/1/encounters/?source=odk&encounter_type=tracks](/api/1/encounters/?source=odk&encounter_type=tracks)

    # date
    * [``/api/1/encounters/?when__year__in=2017,2018``](/api/1/encounters/?when__year__in=2017,2018) Years 2017-18

    # area and site
    For convenience and performance, every Encounter links to the general area of its occurrence (Locality)
    as well as the site it was observed in, if known.
    Encounters can filtered to a Locality or Site via the respective area"s ID.

    * Find your Locality"s ID in
      [/api/1/areas/?area_type=Locality](/api/1/areas/?area_type=Locality)
    * Find your Site"s ID in
      [/api/1/areas/?area_type=Site](/api/1/areas/?area_type=Site)
    * [/api/1/encounters/?site=19](/api/1/encounters/?site=19) Cable Beach Broome
    * [/api/1/encounters/?site=13](/api/1/encounters/?site=13) Port Hedland
    * [/api/1/encounters/?site=13](/api/1/encounters/?site=16) Karratha (Rosemary Is, Burrup)
    * [/api/1/encounters/?site=17](/api/1/encounters/?site=17) Thevenard Island
    * All Encounters within Site 31 ("Broome DBCA Office and Training Area"):
      [/api/1/encounters/?site=31](/api/1/encounters/?site=31)


    # name
    The derived name of an encountered entity (e.g. animal or logger) is the first associated ID,
    such as a turtle flipper tag.

    Filter options:

    * exact (case sensitive and case insensitive)
    * contains (case sensitive and case insensitive)
    * startswith / endwith

    * [/api/1/encounters/?name=WA49138](/api/1/encounters/?name=WA49138)
      Encounters with name "WA49138"
    * [/api/1/encounters/?name__startswith=WA49](/api/1/encounters/?name__startswith=WA49)
      Encounters with name starting with "WA49"
    * [/api/1/encounters/?name__icontains=4913](/api/1/encounters/?name__icontains=4913)
      Encounters with name containing (case-insensitive) "4913"

    # source_id
    The source_id is constructed from coordinates, date, entity and other properties.
    Filter options and examples: see name, substitute "name" with "source_id" and choose
    appropriate filter string values.

    # comments
    Where data are captured digitally, the username is guessed from data collecctors" supplied names.
    This process sometimes goes wrong, and a log is kept in comments.

    * [/api/1/encounters/?comments__icontains=QA](/api/1/encounters/?comments__icontains=QA)
      These encounters require proofreading of usernames.

    Process:

    * Curators can filter Encounters with "TODO" in comments further down to their area,
      of which they know the data collection team.
    * Where the username has no match, the curator can add a new user (with username: givenname_surname) at
      [/admin/users/user/](/admin/users/user/).
    * Where there are multiple matches, the curator can set the correct user at
      [/admin/observations/encounter/](/admin/observations/encounter/)
      plus the Encounter ID and then mark the Encounter as "proofread" to protect the change from
      being overwritten through repeated data imports.

    # source

    * [/api/1/encounters/?source=direct](/api/1/encounters/?source=direct) (direct entry)
    * [/api/1/encounters/?source=paper](/api/1/encounters/?source=paper) (typed off datasheet)
    * [/api/1/encounters/?source=odk](/api/1/encounters/?source=odk) (imported from OpenDataKit digital data capture)
    * [/api/1/encounters/?source=wamtram](/api/1/encounters/?source=wamtram)
      (imported from WAMTRAM turtle tagging database)
    * [/api/1/encounters/?source=ntp-exmouth](/api/1/encounters/?source=ntp-exmouth)
      (imported from MS Access Exmouth tracks database)
    * [/api/1/encounters/?source=ntp-broome](/api/1/encounters/?source=ntp-broome)
      (imported from MS Access Broome tracks database)
    * [/api/1/encounters/?source=cet](/api/1/encounters/?source=cet)
      (imported from FileMaker Pro Cetacean strandings database)
    * [/api/1/encounters/?source=pin](/api/1/encounters/?source=pin)
      (imported from FileMaker Pro Pinnniped strandings database)

    # encounter_type

    * [/api/1/encounters/?encounter_type=stranding](/api/1/encounters/?encounter_type=stranding) (strandings)
    * [/api/1/encounters/?encounter_type=tagging](/api/1/encounters/?encounter_type=tagging) (turtle tagging)
    * [/api/1/encounters/?encounter_type=inwater](/api/1/encounters/?encounter_type=inwater) (in water encounter)
    * [/api/1/encounters/?encounter_type=nest](/api/1/encounters/?encounter_type=nest) (track census, turtle nest)
    * [/api/1/encounters/?encounter_type=tracks](/api/1/encounters/?encounter_type=tracks)
      (track census, track without nest)
    * [/api/1/encounters/?encounter_type=tag-management](/api/1/encounters/?encounter_type=tag-management)
      (admin, tag or sensor asset management task)
    * [/api/1/encounters/?encounter_type=logger](/api/1/encounters/?encounter_type=logger) (tag or logger encounter)
    * [/api/1/encounters/?encounter_type=other](/api/1/encounters/?encounter_type=other) (anything not in above)


    # status

    * [/api/1/encounters/?status=new](/api/1/encounters/?status=new) (Records freshly created or imported)
    * [/api/1/encounters/?status=proofread](/api/1/encounters/?status=proofread)
      (Records marked as proofread = as on paper datasheet)
    * [/api/1/encounters/?status=curated](/api/1/encounters/?status=curated)
      (Records marked as curated = as true as we can make it)
    * [/api/1/encounters/?status=published](/api/1/encounters/?status=published)
      (Records marked ready for public release)

    # location_accuracy

    * [/api/1/encounters/?location_accuracy=10](/api/1/encounters/?location_accuracy=10) (captured via GPS)
    * [/api/1/encounters/?location_accuracy=1000](/api/1/encounters/?location_accuracy=1000) (captured as site name)
    * [/api/1/encounters/?location_accuracy=10000](/api/1/encounters/?location_accuracy=10000) (rough guess)

    # observer and reporter

    * [/api/1/encounters/?observer=100](/api/1/encounters/?observer=100) Observer with ID 100
    * [/api/1/encounters/?reporter=100](/api/1/encounters/?reporter=100) Reporter with ID 100
    """

    latex_name = "latex/encounter.tex"
    queryset = models.Encounter.objects.all().prefetch_related(
        "reporter", "observer", "area", "site",
        "survey", "survey__reporter", "survey__site", "survey__team"
    )
    serializer_class = serializers.EncounterSerializer
    search_fields = ("name", "source_id", )

    bbox_filter_field = "where"
    # bbox_filter_include_overlapping = True
    pagination_class = MyGeoJsonPagination
    filter_class = EncounterFilter
    model = models.Encounter

    def pre_latex(self, t_dir, data):
        """Symlink photographs to temp dir for use by latex template."""
        symlink_resources(t_dir, data)


class FastEncounterViewSet(ModelViewSet):
    """A minimal Encounter viewset.

    Use this viewset to download a minimal useable set of Encounter records.
    This viewset is used in Observation viewsets to form a standalone dataset.
    """
    latex_name = "latex/encounter_fast.tex"
    queryset = models.Encounter.objects.all().prefetch_related(
        "observer", "reporter", "survey", "site", "area", "survey__reporter"
    )
    serializer_class = serializers.FastEncounterSerializer
    search_fields = ("name", "source_id", )

    bbox_filter_field = "where"
    # bbox_filter_include_overlapping = True
    pagination_class = MyGeoJsonPagination
    filter_class = FastEncounterFilter

    def pre_latex(self, t_dir, data):
        """Symlink photographs to temp dir for use by latex template."""
        pass


class SourceIdEncounterViewSet(ModelViewSet):
    """A minimal Encounter viewset showing source and source ID.

    Use this viewset to download a minimal set of Encounter records
    to determine skip logic:
    existing records can be updated (if new) or skipped (if QA'd),
    non-existing records can be created.
    """
    latex_name = "latex/encounter_fast.tex"
    queryset = models.Encounter.objects.all()
    serializer_class = serializers.SourceIdEncounterSerializer
    search_fields = ("name", "source_id", )

    bbox_filter_field = "where"
    # bbox_filter_include_overlapping = True
    pagination_class = MyGeoJsonPagination
    filter_class = FastEncounterFilter

    def pre_latex(self, t_dir, data):
        """Symlink photographs to temp dir for use by latex template."""
        pass


class AnimalEncounterFilter(FilterSet):
    when = DateFilter()

    class Meta:
        model = models.AnimalEncounter
        fields = {
            "encounter_type": ["iexact", "icontains"],
            "status": ["iexact", "icontains"],
            "area": "__all__",
            "site": "__all__",
            "survey": "__all__",
            "source": ["iexact", "icontains"],
            "source_id": "__all__",
            "location_accuracy": ["iexact", "icontains"],
            "when": "__all__",
            "name": "__all__",
            "observer": "__all__",
            "reporter": "__all__",
            "taxon": ["iexact", "icontains"],
            "species": ["iexact", "icontains"],
            "health": ["iexact", "icontains"],
            "sex": ["iexact", "icontains"],
            "maturity": ["iexact", "icontains"],
            "habitat": ["iexact", "icontains"],
            "sighting_status":["iexact", "icontains"],
            "sighting_status_reason":["iexact", "icontains"],
            "identifiers":["iexact", "icontains"],
            "checked_for_injuries": ["iexact", "icontains"],
            "scanned_for_pit_tags": ["iexact", "icontains"],
            "checked_for_flipper_tags": ["iexact", "icontains"],
            "cause_of_death": ["iexact", "icontains"],
            "cause_of_death_confidence": ["iexact", "icontains"],
        }


class AnimalEncounterViewSet(BatchUpsertViewSet):
    """AnimalEncounter view set.

    AnimalEncounters come from marine wildlife incidents (strandings and rescues),
    turtle tagging, and turtle sightings.

    # Filters
    In addition to the filters documented at [/api/1/encounters/](/api/1/encounters/):

    # taxon
    * [/api/1/turtle-nest-encounters/?taxon=Cheloniidae](/api/1/turtle-nest-encounters/?taxon=Cheloniidae)
      Marine Turtles
    * [/api/1/turtle-nest-encounters/?taxon=Cetacea](/api/1/turtle-nest-encounters/?taxon=Cetacea)
      Whales and Dolphins
    * [/api/1/turtle-nest-encounters/?taxon=Pinnipedia](/api/1/turtle-nest-encounters/?taxon=Pinnipedia) Seals
    * [/api/1/turtle-nest-encounters/?taxon=Sirenia](/api/1/turtle-nest-encounters/?taxon=Sirenia) Dugongs
    * [/api/1/turtle-nest-encounters/?taxon=Elasmobranchii](/api/1/turtle-nest-encounters/?taxon=Elasmobranchii)
      Sharks and Rays
    * [/api/1/turtle-nest-encounters/?taxon=Hydrophiinae](/api/1/turtle-nest-encounters/?taxon=Hydrophiinae)
      Sea snakes and kraits

    # species
    * [/api/1/turtle-nest-encounters/?species=natator-depressus](
      /api/1/turtle-nest-encounters/?species=natator-depressus) Flatback turtle
    * [/api/1/turtle-nest-encounters/?species=chelonia-mydas](
      /api/1/turtle-nest-encounters/?species=chelonia-mydas) Green turtle
    * [/api/1/turtle-nest-encounters/?species=eretmochelys-imbricata](
      /api/1/turtle-nest-encounters/?species=eretmochelys-imbricata) Hawksbill turtle
    * [/api/1/turtle-nest-encounters/?species=caretta-caretta](
      /api/1/turtle-nest-encounters/?species=caretta-caretta) Loggerhead turtle
    * [/api/1/turtle-nest-encounters/?species=lepidochelys-olivacea](
      /api/1/turtle-nest-encounters/?species=lepidochelys-olivacea) Olive ridley turtle
    * [/api/1/turtle-nest-encounters/?species=corolla-corolla](
      /api/1/turtle-nest-encounters/?species=corolla-corolla) Hatchback turtle (training dummy)


    # Other filters
    Other enabled filters (typically these categories will be used later during analysis):

    "health", "sex", "maturity", "checked_for_injuries", "scanned_for_pit_tags",
    "checked_for_flipper_tags", "cause_of_death", "cause_of_death_confidence",
    "sighting_status", "sighting_status_reason", "identifiers"
    """

    latex_name = "latex/animalencounter.tex"
    queryset = models.AnimalEncounter.objects.all().prefetch_related(
        "observer", "reporter", "survey", "site", "area", "survey__reporter",
        "site_of_first_sighting", "site_of_last_sighting",
    )
    serializer_class = serializers.AnimalEncounterSerializer
    filter_class = AnimalEncounterFilter
    search_fields = ("name", "source_id", "behaviour", )
    pagination_class = MyGeoJsonPagination
    model = models.AnimalEncounter

    def pre_latex(self, t_dir, data):
        """Symlink photographs to temp dir for use by latex template."""
        symlink_resources(t_dir, data)


class TurtleNestEncounterFilter(FilterSet):
    when = DateFilter()

    class Meta:
        model = models.TurtleNestEncounter
        fields = {
            "area": "__all__",
            "encounter_type": ["iexact", "icontains"],
            "status": ["iexact", "icontains"],
            "site": "__all__",
            "survey": "__all__",
            "source": ["iexact", "icontains"],
            "source_id": "__all__",
            "location_accuracy": "__all__",
            "when": "__all__",
            "name": "__all__",
            "observer": "__all__",
            "reporter": "__all__",
            "nest_age": ["iexact", "icontains"],
            "nest_type": ["iexact", "icontains"],
            "species": ["iexact", "icontains"],
            "habitat": ["iexact", "icontains"],
            "disturbance": ["iexact", "icontains"],
            'nest_tagged': ["iexact", "icontains"],
            'logger_found': ["iexact", "icontains"],
            'eggs_counted': ["iexact", "icontains"],
            'hatchlings_measured': ["iexact", "icontains"],
            'fan_angles_measured': ["iexact", "icontains"],
            "comments": ["icontains"],
        }


class TurtleNestEncounterViewSet(BatchUpsertViewSet):
    """TurtleNestEncounter view set.

    TNE are turtle tracks with or without nests.
    A TNE can include multiple observations (disturbance, nest tag, egg count,
    hatchling morph, fan angles etc).

    # Filters
    In addition to the filters documented at [/api/1/encounters/](/api/1/encounters/):

    # nest_age
    * [/api/1/turtle-nest-encounters/?nest_age=fresh](/api/1/turtle-nest-encounters/?nest_age=fresh)
      observed in the morning, made the night before (same turtle date)
    * [/api/1/turtle-nest-encounters/?nest_age=old](/api/1/turtle-nest-encounters/?nest_age=old)
      older than a day (previous turtle date)
    * [/api/1/turtle-nest-encounters/?nest_age=unknown](/api/1/turtle-nest-encounters/?nest_age=unknown)
      unknown
    * [/api/1/turtle-nest-encounters/?nest_age=missed](/api/1/turtle-nest-encounters/?nest_age=missed)
      missed turtle during turtle tagging, track observed and made within same night (same turtle date)

    # nest_type
    * [/api/1/turtle-nest-encounters/?nest_type=track-not-assessed](
      /api/1/turtle-nest-encounters/?nest_type=track-not-assessed) track, not checked for nest
    * [/api/1/turtle-nest-encounters/?nest_type=false-crawl](
      /api/1/turtle-nest-encounters/?nest_type=false-crawl) track without nest
    * [/api/1/turtle-nest-encounters/?nest_type=successful-crawl](
      /api/1/turtle-nest-encounters/?nest_type=successful-crawl) track with nest
    * [/api/1/turtle-nest-encounters/?nest_type=track-unsure](
      /api/1/turtle-nest-encounters/?nest_type=track-unsure) track, checked for nest, unsure if nest
    * [/api/1/turtle-nest-encounters/?nest_type=nest](
      /api/1/turtle-nest-encounters/?nest_type=nest) nest, unhatched, no track
    * [/api/1/turtle-nest-encounters/?nest_type=hatched-nest](
      /api/1/turtle-nest-encounters/?nest_type=hatched-nest) nest, hatched
    * [/api/1/turtle-nest-encounters/?nest_type=body-pit](
      /api/1/turtle-nest-encounters/?nest_type=body-pit) body pit, no track

    # species
    * [/api/1/turtle-nest-encounters/?species=natator-depressus](
      /api/1/turtle-nest-encounters/?species=natator-depressus) Flatback turtle
    * [/api/1/turtle-nest-encounters/?species=chelonia-mydas](
      /api/1/turtle-nest-encounters/?species=chelonia-mydas) Green turtle
    * [/api/1/turtle-nest-encounters/?species=eretmochelys-imbricata](
      /api/1/turtle-nest-encounters/?species=eretmochelys-imbricata) Hawksbill turtle
    * [/api/1/turtle-nest-encounters/?species=caretta-caretta](
      /api/1/turtle-nest-encounters/?species=caretta-caretta) Loggerhead turtle
    * [/api/1/turtle-nest-encounters/?species=lepidochelys-olivacea](
      /api/1/turtle-nest-encounters/?species=lepidochelys-olivacea) Olive ridley turtle
    * [/api/1/turtle-nest-encounters/?species=corolla-corolla](
      /api/1/turtle-nest-encounters/?species=corolla-corolla) Hatchback turtle (training dummy)

    # habitat
    * [/api/1/turtle-nest-encounters/?habitat=na](
      /api/1/turtle-nest-encounters/?habitat=na) unknown habitat
    * [/api/1/turtle-nest-encounters/?habitat=beach-below-high-water](
      /api/1/turtle-nest-encounters/?habitat=beach-below-high-water) beach below high water mark
    * [/api/1/turtle-nest-encounters/?habitat=beach-above-high-water](
      /api/1/turtle-nest-encounters/?habitat=beach-above-high-water) beach above high water mark and dune
    * [/api/1/turtle-nest-encounters/?habitat=beach-edge-of-vegetation](
      /api/1/turtle-nest-encounters/?habitat=beach-edge-of-vegetation) edge of vegetation
    * [/api/1/turtle-nest-encounters/?habitat=in-dune-vegetation](
      /api/1/turtle-nest-encounters/?habitat=in-dune-vegetation) inside vegetation

    # disturbance
    Indicates whether disturbance observation is attached.

    * [/api/1/turtle-nest-encounters/?disturbance=present](/api/1/turtle-nest-encounters/?disturbance=present) present
    * [/api/1/turtle-nest-encounters/?disturbance=absent](/api/1/turtle-nest-encounters/?disturbance=absent) absent
    * [/api/1/turtle-nest-encounters/?disturbance=na](/api/1/turtle-nest-encounters/?disturbance=na) na

    # name
    * [/api/1/turtle-nest-encounters/?name=WA1234](/api/1/turtle-nest-encounters/?name=WA1234) Turtle name if known

    [Admin](/admin/observations/turtlenestencounter/)
    """
    latex_name = "latex/turtlenestencounter.tex"
    queryset = models.TurtleNestEncounter.objects.all().prefetch_related(
        "observer", "reporter", "survey", "site", "area", "survey__reporter"
    )
    serializer_class = serializers.TurtleNestEncounterSerializer
    filter_class = TurtleNestEncounterFilter
    pagination_class = MyGeoJsonPagination
    model = models.TurtleNestEncounter

    def pre_latex(self, t_dir, data):
        """Symlink photographs to temp dir for use by latex template."""
        symlink_resources(t_dir, data)


class LineTransectEncounterViewSet(BatchUpsertViewSet):
    # latex_name = "latex/loggerencounter.tex"
    queryset = models.LineTransectEncounter.objects.all().prefetch_related(
        "observer", "reporter", "survey", "site", "area", "survey__reporter"
    )
    serializer_class = serializers.LineTransectEncounterSerializer
    filter_fields = ["encounter_type",
                     "status", "area", "site", "survey", "source", "source_id",
                     "location_accuracy", "when", "name", "observer", "reporter",
                     "comments"]
    search_fields = ("name", "source_id", )
    pagination_class = MyGeoJsonPagination
    model = models.LineTransectEncounter

    def pre_latex(self, t_dir, data):
        """Symlink photographs to temp dir for use by latex template."""
        symlink_resources(t_dir, data)


# class LoggerEncounterViewSet(BatchUpsertViewSet):
#     latex_name = "latex/loggerencounter.tex"
#     queryset = models.LoggerEncounter.objects.all().prefetch_related(
#         "observer", "reporter", "survey", "site", "area", "survey__reporter"
#     )
#     serializer_class = serializers.LoggerEncounterSerializer
#     filter_fields = ["encounter_type",
#                      "status", "area", "site", "survey", "source", "source_id",
#                      "location_accuracy", "when", "name", "observer", "reporter",
#                      "deployment_status", "comments"]
#     search_fields = ("name", "source_id", )
#     pagination_class = MyGeoJsonPagination
#     model = models.LoggerEncounter

#     def pre_latex(self, t_dir, data):
#         """Symlink photographs to temp dir for use by latex template."""
#         symlink_resources(t_dir, data)


class ObservationViewSet(ObservationBatchUpsertViewSet):
    """Generic list of Observations.

    [Admin](/admin/observations/)
    """
    queryset = models.Observation.objects.all()
    serializer_class = serializers.ObservationSerializer
    model = models.Observation


class MediaAttachmentViewSet(ModelViewSet):
    """Binary media (photos, datasheet PDFs etc) with Encounter details.

    Can be many per Encounter.
    [Admin](/admin/observations/media-attachments/)
    """
    queryset = models.MediaAttachment.objects.all().prefetch_related(
        "encounter__observer", "encounter__reporter",
        "encounter__survey", "encounter__survey__reporter",
        "encounter__site", "encounter__area",
    )
    serializer_class = serializers.MediaAttachmentSerializer
    pagination_class = MyGeoJsonPagination
    parser_classes = [FormParser, MultiPartParser]
    model = models.MediaAttachment


class TagObservationViewSet(ObservationBatchUpsertViewSet):
    """An Observation of an identifying tag on an observed entity including Encounter details.

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

    * `#` = tag attached new, number NA, need to double-check number
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

    Can be many per Encounter.
    [Admin](/admin/observations/tagobservation/)
    """
    queryset = models.TagObservation.objects.all().prefetch_related(
        "encounter__observer", "encounter__reporter",
        "encounter__survey", "encounter__survey__reporter",
        "encounter__site", "encounter__area",
        "handler", "recorder")
    serializer_class = serializers.TagObservationSerializer
    filter_fields = [
        "encounter__area",
        "encounter__site",
        "encounter__encounter_type",
        "handler",
        "recorder",
        "tag_type",
        "tag_location",
        "name",
        "status",
        "comments"]
    search_fields = ("name", "comments", )
    pagination_class = MyGeoJsonPagination
    model = models.TagObservation


class NestTagObservationViewSet(ObservationBatchUpsertViewSet):
    """NestTagObservations are sightings of tags on a turtle nest.

    Nest tags allow to connect multiple sightings of a nest with the same tag
    into a contiguous record.

    Nest tags have a life cycle which includes application and resighting.

    Typically one, but can be many per Encounter.
    [Admin](/admin/observations/nesttagobservation/)
    """
    queryset = models.NestTagObservation.objects.all().prefetch_related(
        "encounter__observer", "encounter__reporter",
        "encounter__survey", "encounter__survey__reporter",
        "encounter__site", "encounter__area",
    )
    serializer_class = serializers.NestTagObservationSerializer
    filter_fields = ["encounter__area", "encounter__site", "encounter__encounter_type",
                     "status", "flipper_tag_id", "date_nest_laid", "tag_label", "comments"]
    pagination_class = MyGeoJsonPagination
    model = models.NestTagObservation


class ManagementActionViewSet(ObservationBatchUpsertViewSet):
    """ManagementActions following Encounters.

    E.g.: animal rescue, rehab, disposal, euthanasia.
    Sometimes this information is also recorded as Encounter.comments.

    Can be many per Encounter.
    """

    queryset = models.ManagementAction.objects.all().prefetch_related(
        "encounter__observer", "encounter__reporter",
        "encounter__survey", "encounter__survey__reporter",
        "encounter__site", "encounter__area",
    )
    serializer_class = serializers.ManagementActionSerializer
    model = models.ManagementAction


class TurtleDamageObservationViewSet(ObservationBatchUpsertViewSet):
    """Observation of turtle damages or injuries including Encounter details.

    Can be many per Encounter.
    [Admin](/admin/observations/turtledamageobservation/)
    """
    queryset = models.TurtleDamageObservation.objects.all().prefetch_related(
        "encounter__observer", "encounter__reporter",
        "encounter__survey", "encounter__survey__reporter",
        "encounter__site", "encounter__area",
    )
    serializer_class = serializers.TurtleDamageObservationSerializer
    filter_fields = [
        "encounter__area",
        "encounter__site",
        "encounter__encounter_type",
        "encounter__status"
    ]
    pagination_class = MyGeoJsonPagination
    model = models.TurtleDamageObservation


class TurtleMorphometricObservationViewSet(ObservationBatchUpsertViewSet):
    """Morphometric measurements of a turtle including Encounter details.

    [Admin](/admin/observations/turtlemorphometricobservation/)
    """
    queryset = models.TurtleMorphometricObservation.objects.all().prefetch_related(
        "encounter__observer", "encounter__reporter",
        "encounter__survey", "encounter__survey__reporter",
        "encounter__site", "encounter__area",
        "handler", "recorder"
    )
    serializer_class = serializers.TurtleMorphometricObservationSerializer
    filter_fields = [
        "encounter__area",
        "encounter__site",
        "encounter__encounter_type",
        "encounter__status"
    ]
    search_fields = ("comments", )
    pagination_class = MyGeoJsonPagination
    model = models.TurtleMorphometricObservation


class HatchlingMorphometricObservationViewSet(ObservationBatchUpsertViewSet):
    """Morphometric measurements of a hatchling including Encounter details.

    Can be many per Encounter.
    [Admin](/admin/observations/hatchlingmorphometricobservation/)
    """
    queryset = models.HatchlingMorphometricObservation.objects.all().prefetch_related(
        "encounter", "encounter__observer", "encounter__reporter",
        "encounter__survey", "encounter__survey__reporter", "encounter__site", "encounter__area")
    serializer_class = serializers.HatchlingMorphometricObservationSerializer
    filter_fields = ["encounter__area", "encounter__site", "encounter__encounter_type", ]
    pagination_class = MyGeoJsonPagination
    model = models.HatchlingMorphometricObservation


class TurtleNestObservationViewSet(ObservationBatchUpsertViewSet):
    """Nest excavations during tagging or after hatching including Encounter details.

    Egg count is done as total, plus categories of nest contents following
    "Determining Clutch Size and Hatching Success, Jeffrey D. Miller,
    Research and Management Techniques for the Conservation of Sea Turtles,
    IUCN Marine Turtle Specialist Group, 1999.

    Typically one per Encounter.
    [Admin](/admin/observations/turtlenestobservation/)
    """

    queryset = models.TurtleNestObservation.objects.all().prefetch_related(
        "encounter", "encounter__observer", "encounter__reporter",
        "encounter__survey", "encounter__survey__reporter",
        "encounter__site", "encounter__area")
    serializer_class = serializers.TurtleNestObservationSerializer
    filter_fields = [
        "encounter__area",
        "encounter__site",
        "encounter__encounter_type",
        "encounter__status",
        "eggs_laid",
    ]
    search_fields = ("comments", )
    pagination_class = MyGeoJsonPagination
    model = models.TurtleNestObservation


class TurtleNestDisturbanceObservationViewSet(ObservationBatchUpsertViewSet):
    """Turtle nest disturbance observations including Encounter details.

    * General disturbances are of Encounter type
      [other](/api/1/turtle-nest-disturbance-observations/?encounter__encounter_type=other)
    * Nest disturbances are of Encounter type
      [nest](/api/1/turtle-nest-disturbance-observations/?encounter__encounter_type=nest)

    Can be many per Encounter.
    [Admin](/admin/observations/turtlenestdisturbanceobservation/)
    """
    queryset = models.TurtleNestDisturbanceObservation.objects.all().prefetch_related(
        "encounter", "encounter__observer", "encounter__reporter",
        "encounter__survey", "encounter__survey__reporter",
        "encounter__site", "encounter__area")
    serializer_class = serializers.TurtleNestDisturbanceObservationSerializer
    filter_fields = [
        "encounter__area",
        "encounter__site",
        "encounter__encounter_type",
        "encounter__status",
        "disturbance_cause",
        "disturbance_cause_confidence",
        "disturbance_severity",
    ]
    pagination_class = MyGeoJsonPagination
    model = models.TurtleNestDisturbanceObservation


class TurtleHatchlingEmergenceObservationViewSet(ObservationBatchUpsertViewSet):
    """Turtle hatchling emergence observation (fan angles) including Encounter details.

    Typically one per Encounter.
    [Admin](/admin/observations/turtlehatchlingemergenceobservation/)
    """
    queryset = models.TurtleHatchlingEmergenceObservation.objects.all().prefetch_related(
        "encounter", "encounter__observer", "encounter__reporter",
        "encounter__survey", "encounter__survey__reporter",
        "encounter__site", "encounter__area")
    serializer_class = serializers.TurtleHatchlingEmergenceObservationSerializer
    filter_fields = ["encounter__area", "encounter__site", "encounter__encounter_type", ]
    pagination_class = MyGeoJsonPagination
    model = models.TurtleHatchlingEmergenceObservation


class TurtleHatchlingEmergenceOutlierObservationViewSet(ObservationBatchUpsertViewSet):
    """Fan angle outliers including Encounter details.

    Can be many per Encounter.
    [Admin](/admin/observations/turtlehatchlingemergenceoutlierobservation/)
    """
    queryset = models.TurtleHatchlingEmergenceOutlierObservation.objects.all().prefetch_related(
        "encounter", "encounter__observer", "encounter__reporter",
        "encounter__survey", "encounter__survey__reporter",
        "encounter__site", "encounter__area")
    serializer_class = serializers.TurtleHatchlingEmergenceOutlierObservationSerializer
    filter_fields = ["encounter__area", "encounter__site", "encounter__encounter_type", ]
    pagination_class = MyGeoJsonPagination
    model = models.TurtleHatchlingEmergenceOutlierObservation


class LightSourceObservationViewSet(ObservationBatchUpsertViewSet):
    """Known light sources during turtle hatching including Encounter details.

    Can be many per Encounter.
    [Admin](/admin/observations/lightsourceobservation/)
    """
    queryset = models.LightSourceObservation.objects.all().prefetch_related(
        "encounter", "encounter__observer", "encounter__reporter",
        "encounter__survey", "encounter__survey__reporter",
        "encounter__site", "encounter__area")
    serializer_class = serializers.LightSourceObservationSerializer
    filter_fields = ["encounter__area", "encounter__site", "encounter__encounter_type", ]
    pagination_class = MyGeoJsonPagination
    model = models.LightSourceObservation


class LoggerObservationViewSet(ObservationBatchUpsertViewSet):
    """Logger observations.

    Can be many per Encounter.
    [Admin](/admin/observations/loggerobservation/)
    """
    queryset = models.LoggerObservation.objects.all().prefetch_related(
        "encounter", "encounter__observer", "encounter__reporter",
        "encounter__survey", "encounter__survey__reporter",
        "encounter__site", "encounter__area")
    serializer_class = serializers.LoggerObservationSerializer
    filter_fields = ["encounter__area", "encounter__site", "encounter__encounter_type", ]
    pagination_class = MyGeoJsonPagination
    model = models.LoggerObservation


class TrackTallyObservationViewSet(ObservationBatchUpsertViewSet):
    """A turtle track tally from a LineTransectEncounter.

    Can be many per Encounter.
    Admin: see Encounter inlines.
    """
    queryset = models.TrackTallyObservation.objects.all().prefetch_related(
        "encounter", "encounter__observer", "encounter__reporter",
        "encounter__survey", "encounter__survey__reporter",
        "encounter__site", "encounter__area")
    serializer_class = serializers.TrackTallyObservationSerializer
    filter_fields = ["encounter__area", "encounter__site", "encounter__encounter_type", ]
    pagination_class = MyGeoJsonPagination
    model = models.TrackTallyObservation


class TurtleNestDisturbanceTallyObservationViewSet(ObservationBatchUpsertViewSet):
    """A turtle nest disturbance tally from a LineTransectEncounter.

    Can be many per Encounter.
    Admin: see Encounter inlines.
    """
    queryset = models.TurtleNestDisturbanceTallyObservation.objects.all().prefetch_related(
        "encounter", "encounter__observer", "encounter__reporter",
        "encounter__survey", "encounter__survey__reporter",
        "encounter__site", "encounter__area")
    serializer_class = serializers.TurtleNestDisturbanceTallyObservationSerializer
    filter_fields = ["encounter__area", "encounter__site", "encounter__encounter_type", ]
    pagination_class = MyGeoJsonPagination
    model = models.TurtleNestDisturbanceTallyObservation
