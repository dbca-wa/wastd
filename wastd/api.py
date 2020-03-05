# -*- coding: utf-8 -*-
"""The WAStD API.

* Encouter and subclasses: AnimalEncounter, TurtleNestEncounter
* Encounter Inlines: Observation subclasses
* Separate TagObservation serializer to retrieve a Tag history
* Taxonomic names

This API outputs:

* Interactive HTML API
* CSV
* JSONP
* Latex (coming soon)

This API is built using:

* djangorestframework
* `djangorestframework-gis <https://github.com/djangonauts/django-rest-framework-gis>`_
* djangorestframework-csv
* `djangorestframework-yaml <http://www.django-rest-framework.org/api-guide/renderers/#yaml>`_ (TODO support geo field)
* djangorestframework-jsonp
* django-rest-polymorphic <https://github.com/apirobot/django-rest-polymorphic>
* django-url-filter
* dynamic-rest (not used)
* rest-framework-latex
* markdown
* django-filter
* django-rest-swagger
* coreapi
* coreapi-cli (complementary CLI for coreapi)
"""
# from django.shortcuts import render
import logging

import rest_framework_filters as filters
# from django.db import models as django_models
from django.template import Context, Template
# from django.db.models import Prefetch

# import django_filters as df
from django_filters import rest_framework as rf_filters
from rest_framework import pagination, routers, serializers, status, viewsets
from rest_framework.response import Response as RestResponse
from rest_framework_gis.fields import GeometryField
from rest_framework_gis.filters import InBBoxFilter
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from taxonomy.models import (
    Community,
    Crossreference,
    HbvFamily,
    HbvGenus,
    HbvGroup,
    HbvName,
    HbvParent,
    HbvSpecies,
    HbvSupra,
    HbvVernacular,
    HbvXref,
    Taxon,
    Vernacular,
)

# from taxonomy.filters import TaxonFilter as djangofilter_TaxonFilter

from shared.api import (
    BatchUpsertViewSet,
    NameIDBatchUpsertViewSet,
    OgcFidBatchUpsertViewSet,
    MyGeoJsonPagination,
)
# from shared.models import QualityControlMixin
from wastd.observations.models import Observation  # LineTransectEncounter
from wastd.observations.models import Survey  # SiteVisit,
from wastd.observations.models import (
    AnimalEncounter,
    Area,
    DispatchRecord,
    DugongMorphometricObservation,
    Encounter,
    HatchlingMorphometricObservation,
    LoggerEncounter,
    ManagementAction,
    MediaAttachment,
    NestTagObservation,
    TagObservation,
    TemperatureLoggerDeployment,
    TemperatureLoggerSettings,
    TrackTallyObservation,
    TurtleDamageObservation,
    TurtleMorphometricObservation,
    TurtleNestDisturbanceObservation,
    TurtleNestDisturbanceTallyObservation,
    TurtleNestEncounter,
    TurtleNestObservation,
    TurtleHatchlingEmergenceObservation,
    TurtleHatchlingEmergenceOutlierObservation,
    LightSourceObservation
)
from wastd.users.models import User

# from rest_framework.renderers import BrowsableAPIRenderer
# from rest_framework_latex import renderers
# from dynamic_rest import serializers as ds, viewsets as dv
# from drf_extra_fields.geo_fields import PointField
# from rest_framework_gis.pagination import GeoJsonPagination
# from rest_framework_gis.filterset import GeoFilterSet
# from wastd.observations.filters import AreaFilter, LocationListFilter, EncounterFilter
try:
    from wastd.observations.utils import symlink_resources
except BaseException:
    # Docker image build migrate falls over this import
    pass

logger = logging.getLogger(__name__)

# def symlink_resources(a,b,c):
#     pass

# from django.conf import settings

# from synctool.routing import Route as SynctoolRoute
# # Synctools
# # http://django-synctool.readthedocs.io/
# sync_route = SynctoolRoute()
# @sync_route.app("users", "users")
# @sync_route.app("observations", "observations")

router = routers.DefaultRouter()


class InBBoxHTMLMixin:
    """Mixin for bbox search."""

    template = Template("""
    {% load i18n %}
    <style type="text/css">
    # geofilter input[type="text"]{
        width: 100px;
    }
    </style>
    <h2>{% trans "Limit results to area" %}</h2>
    <form id="geofilter" action="" method="get">

        <div class="form-group row">
            <div class="col-md-2"></div>
            <div class="col-md-2">
            <div class="controls">
            <input type="text" class="form-control" id="gf-north" placeholder="North">
            </div>
            </div>
        </div>

        <div class="form-group row">
            <div class="col-md-2">
            <div class="controls">
            <input type="text" class="form-control" id="gf-west" placeholder="West">
            </div>
            </div>

            <div class="col-md-2"></div>
            <div class="col-md-2">
            <div class="controls">
            <input type="text" class="form-control" id="gf-east" placeholder="East">
            </div>
            </div>
        </div>

        <div class="form-group row">
            <div class="col-md-2"></div>
            <div class="col-md-2">
            <div class="controls">
            <input type="text" class="form-control" id="gf-south" placeholder="South">
            </div>
            </div>
        </div>

        <input id="gf-result" type="hidden" name="{{bbox_param}}">
        <button type="submit" class="btn btn-primary">{% trans "Submit" %}
        </button>
    </form>
    <script language="JavaScript">
    (function() {
        document.getElementById("geofilter").onsubmit = function(){
            var result = document.getElementById("gf-result");
            var box = [
                document.getElementById("gf-south").value,
                document.getElementById("gf-west").value,
                document.getElementById("gf-north").value,
                document.getElementById("gf-east").value
            ];
            if(!box.every(function(i){ return i.length }))
                return false;
            result.value = box.join(",");
        }
    })();
    </script>
    """)

    def to_html(self, request, queryset, view):
        """Representation as HTML."""
        return self.template.render(Context({"bbox_param": self.bbox_param}))


class CustomBBoxFilter(InBBoxHTMLMixin, InBBoxFilter):
    """Custom BBox filter."""

    bbox_param = "in_bbox"


# Users ----------------------------------------------------------------#
class UserSerializer(serializers.ModelSerializer):
    """User serializer."""

    class Meta:
        """Class options."""

        model = User
        fields = ("pk", "username", "name", "nickname", "aliases", "role", "email", "phone", )


class FastUserSerializer(serializers.ModelSerializer):
    """Minimal User serializer."""

    class Meta:
        """Class options."""

        model = User
        fields = ("pk", "username", "name",)


# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    """User view set."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    uid_field = "username"
    model = User

    def create_one(self, data):
        """POST: Create or update exactly one model instance."""
        from wastd.observations.utils import lowersnake
        un = lowersnake(data["name"])

        obj, created = self.model.objects.get_or_create(username=un, defaults=data)
        if not created:
            self.model.objects.filter(username=un).update(**data)

        verb = "Created" if created else "Updated"
        st = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        msg = "[API][UserViewSet][create_one] {0} {1}".format(verb, obj.__str__())
        content = {"id": obj.id, "msg": msg}
        logger.info(msg)

        return RestResponse(content, status=st)

    def create(self, request):
        """POST: Create or update one or many model instances.

        request.data must be:

        * a GeoJSON feature property dict, or
        * a list of GeoJSON feature property dicts.
        """
        # pdb.set_trace()
        if "name" in request.data:
            res = self.create_one(request.data)
            return res
        elif isinstance(request.data, list) and "name" in request.data[1]:
            res = [self.create_one(data) for data in request.data]
            return RestResponse(request.data, status=status.HTTP_200_OK)
        else:
            return RestResponse(request.data, status=status.HTTP_400_BAD_REQUEST)


router.register(r"users", UserViewSet)


# Areas --------------------------------------------------------------------#
class AreaSerializer(GeoFeatureModelSerializer):
    """Area serializer."""

    class Meta:
        """Class options."""

        model = Area
        geo_field = "geom"
        fields = (
            "pk",
            "area_type",
            "name",
            "geom",
            "northern_extent",
            "centroid",
            "length_surveyed_m",
            "length_survey_roundtrip_m"
        )


class FastAreaSerializer(serializers.ModelSerializer):
    """Minimal Area serializer."""

    class Meta:
        """Class options."""

        model = Area
        geo_field = "geom"
        fields = ("pk", "area_type", "name", )


class AreaFilter(filters.FilterSet):
    """Area filter."""

    class Meta:
        """Class opts."""

        model = Area
        fields = {
            "area_type": ["exact", "in", "startswith"],
            "name": ["exact", "iexact", "in", "startswith", "contains", "icontains"],
        }


class AreaViewSet(viewsets.ModelViewSet):
    """Area view set.

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

    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    filter_class = AreaFilter
    bbox_filter_field = "geom"
    pagination_class = MyGeoJsonPagination


router.register(r"area", AreaViewSet)


# Surveys --------------------------------------------------------------------#
class SurveySerializer(GeoFeatureModelSerializer):
    """Survey serializer."""

    reporter = FastUserSerializer(many=False)
    site = FastAreaSerializer(many=False)
    status = serializers.ReadOnlyField()

    class Meta:
        """Class options."""

        model = Survey
        geo_field = "start_location"
        fields = "__all__"


class FastSurveySerializer(serializers.ModelSerializer):
    """Survey serializer."""

    reporter = FastUserSerializer(many=False, read_only=True)
    site = FastAreaSerializer(many=False, read_only=True)

    class Meta:
        """Class options."""

        model = Survey
        fields = [
            "id",
            "site",
            "start_time",
            "end_time",
            "start_comments",
            "end_comments",
            "reporter",
            "absolute_admin_url",
            "production"
        ]


class SurveyFilter(filters.FilterSet):
    """Survey Filter. All filter methods available on all fields except location and team.

    # Dates
    * [/api/1/surveys/?start_time__year__in=2017,2018](/api/1/surveys/?start_time__year__in=2017,2018) Years 2017, 2018
    """

    start_time = rf_filters.DateFilter()
    end_time = rf_filters.DateFilter()

    class Meta:
        """Class opts."""

        model = Survey
        fields = {
            "id": "__all__",
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


class SurveyViewSet(viewsets.ModelViewSet):
    """Survey ModelViewSet.

    All filters are available on all fields except location and team.
    """

    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    filter_class = SurveyFilter
    # pagination_class = pagination.LimitOffsetPagination # provides results$features
    pagination_class = MyGeoJsonPagination  # provides top level features


router.register("surveys", SurveyViewSet)


# Observations ---------------------------------------------------------------#
class ObservationSerializer(serializers.ModelSerializer):
    """The Observation serializer resolves its polymorphic subclasses.

    Observations have polymorphic subclasses (TagObservation, MediaAttachment
    etc.).
    A plain DRF serializer would simply return the shared Observation fields,
    but not the individual fields partial to its subclasses.

    Overriding the `to_representation` method, this serializer tests the
    object to display for its real instance, and calls the `to_representation`
    from the subclasses serializer.

    `Credits <http://stackoverflow.com/a/19976203/2813717>`_
    `Author <http://stackoverflow.com/users/1514427/michael-van-de-waeter>`_
    """

    # as_latex = serializers.ReadOnlyField()

    class Meta:
        """Class options."""

        model = Observation
        fields = ("observation_name",
                  #  "as_latex"
                  )

    def to_representation(self, obj):
        """Resolve the Observation instance to the child class"s serializer."""
        if isinstance(obj, TurtleMorphometricObservation):
            return TurtleMorphometricObservationSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, TurtleDamageObservation):
            return TurtleDamageObservationSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, TurtleNestObservation):
            return TurtleNestObservationSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, ManagementAction):
            return ManagementActionSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, TurtleNestObservation):
            return TurtleNestObservationSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, TurtleNestDisturbanceObservation):
            return TurtleNestDisturbanceObservationSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, TrackTallyObservation):
            return TrackTallyObservationSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, TurtleNestDisturbanceTallyObservation):
            return TurtleNestDisturbanceTallyObservationSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, TagObservation):
            return TagObservationSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, MediaAttachment):
            return MediaAttachmentSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, TemperatureLoggerSettings):
            return TemperatureLoggerSettingsSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, DispatchRecord):
            return DispatchRecordSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, TemperatureLoggerDeployment):
            return TemperatureLoggerDeploymentSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, NestTagObservation):
            return NestTagObservationSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, HatchlingMorphometricObservation):
            return HatchlingMorphometricObservationSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, DugongMorphometricObservation):
            return DugongMorphometricObservationSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, TurtleHatchlingEmergenceObservation):
            return TurtleHatchlingEmergenceObservationSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, TurtleHatchlingEmergenceOutlierObservation):
            return TurtleHatchlingEmergenceOutlierObservationSerializer(
                obj, context=self.context).to_representation(obj)
        if isinstance(obj, LightSourceObservation):
            return LightSourceObservationSerializer(
                obj, context=self.context).to_representation(obj)

        return super(ObservationSerializer, self).to_representation(obj)


class MediaAttachmentSerializer(serializers.ModelSerializer):
    """MediaAttachment serializer."""

    attachment = serializers.FileField(use_url=False)
    filepath = serializers.ReadOnlyField()
    # as_latex = serializers.ReadOnlyField()

    class Meta:
        """Class options."""

        model = MediaAttachment
        fields = ("observation_name",  # "as_latex",
                  "media_type", "title", "attachment", "filepath")
        # fields = "__all__"


class ManagementActionSerializer(serializers.ModelSerializer):
    """DisposalObservation serializer."""

    # as_latex = serializers.ReadOnlyField()

    class Meta:
        """Class options."""

        model = ManagementAction
        fields = ("observation_name",  # "as_latex",
                  "management_actions", "comments", )


class TurtleDamageObservationSerializer(serializers.ModelSerializer):
    """TurtleDamageObservation serializer."""

    # as_latex = serializers.ReadOnlyField()

    class Meta:
        """Class options."""

        model = TurtleDamageObservation
        fields = ("observation_name",  # "as_latex",
                  "body_part", "damage_type", "damage_age", "description", )


class TrackTallyObservationSerializer(serializers.ModelSerializer):
    """TrackTallyObservation serializer."""

    # as_latex = serializers.ReadOnlyField()

    class Meta:
        """Class options."""

        model = TrackTallyObservation
        fields = ("observation_name",  # "as_latex",
                  "species", "nest_type", )


class TurtleNestDisturbanceTallyObservationSerializer(serializers.ModelSerializer):
    """TurtleNestDisturbanceTallyObservation serializer."""

    # as_latex = serializers.ReadOnlyField()

    class Meta:
        """Class options."""

        model = TurtleNestDisturbanceTallyObservation
        fields = ("observation_name",  # "as_latex",
                  "species", "disturbance_cause", )


class TemperatureLoggerSettingsSerializer(serializers.ModelSerializer):
    """TemperatureLoggerSettings serializer."""

    # as_latex = serializers.ReadOnlyField()

    class Meta:
        """Class options."""

        model = TemperatureLoggerSettings
        fields = ("observation_name",  # "as_latex",
                  "logging_interval", "recording_start", "tested", )


class DispatchRecordSerializer(serializers.ModelSerializer):
    """DispatchRecord serializer."""

    # as_latex = serializers.ReadOnlyField()

    class Meta:
        """Class options."""

        model = DispatchRecord
        fields = ("observation_name",  # "as_latex",
                  "sent_to",)


class TemperatureLoggerDeploymentSerializer(serializers.ModelSerializer):
    """TemperatureLoggerDeployment serializer."""

    # as_latex = serializers.ReadOnlyField()

    class Meta:
        """Class options."""

        model = TemperatureLoggerDeployment
        fields = ("observation_name",  # "as_latex", #
                  "depth_mm",
                  "marker1_present",
                  "distance_to_marker1_mm",
                  "marker2_present",
                  "distance_to_marker2_mm",
                  "habitat",
                  "distance_to_vegetation_mm", )


class DugongMorphometricObservationSerializer(serializers.ModelSerializer):
    """DugongMorphometricObservationSerializer."""

    # as_latex = serializers.ReadOnlyField()

    class Meta:
        """Class options."""

        model = DugongMorphometricObservation
        fields = ("observation_name",  # "as_latex", #
                  "body_length_mm",
                  "body_girth_mm",
                  "tail_fluke_width_mm",
                  "tusks_found",
                  )


class EncounterSerializer(GeoFeatureModelSerializer):
    """Encounter serializer.

    Alternative: serializers.HyperlinkedModelSerializer

    TODO: a writable version of the serializer will provide `create` and
    `update` methods, which also create/update the inline Observations.

    Since nested Observations are polymorphic, two steps have to be taken above
    the plain nested writeable API:

    * :mod:`wastd.observations.models.Observation.observation_name` is a property
      method to return the child model"s name
    * :mod:`wastd.api.ObservationSerializer` includes the `observation_name` in
      the API dict
    * :mod:`wastd.api.EncounterSerializer.create` and `update` (coming) handle
      both the Encounter and the nested Observations separately. Observations
      use their included `observation_name` to figure out the actual model that
      we want to `create` or `update`.

      TODO http://stackoverflow.com/q/32123148/2813717
      NOTE this API is not writeable, as related models (User and Observation)
      require customisations to handle data thrown at them.
    """

    observation_set = ObservationSerializer(many=True, read_only=False)
    observer = FastUserSerializer(many=False, read_only=True)
    reporter = FastUserSerializer(many=False, read_only=True)
    area = FastAreaSerializer(many=False, read_only=True)
    site = FastAreaSerializer(many=False, read_only=True)
    survey = FastSurveySerializer(many=False, read_only=True)
    # observer = serializers.StringRelatedField(read_only=True)
    # reporter = serializers.StringRelatedField(read_only=True)
    # where = PointField(required=True)   ## THIS BREAKS GEOJSON OUTPUT
    leaflet_title = serializers.ReadOnlyField()
    latitude = serializers.ReadOnlyField()
    longitude = serializers.ReadOnlyField()
    crs = serializers.ReadOnlyField()
    absolute_admin_url = serializers.ReadOnlyField()
    photographs = MediaAttachmentSerializer(many=True, read_only=False)
    tx_logs = serializers.ReadOnlyField()

    class Meta:
        """Class options.

        The non-standard name `where` is declared as the geo field for the
        GeoJSON serializer"s benefit.
        """

        model = Encounter
        name = "encounter"
        fields = ("pk", "area", "site", "survey",
                  "where", "location_accuracy", "when",
                  "name", "observer", "reporter", "comments",
                  "status", "source", "source_id", "encounter_type",
                  "leaflet_title", "latitude", "longitude", "crs",
                  "absolute_admin_url", "photographs", "tx_logs",
                  #  "as_html", "as_latex",
                  "observation_set", )
        geo_field = "where"
        id_field = "source_id"

    # def create(self, validated_data):
    #     """Make EncounterSerializer writeable: create
    #
    #     POST a set of records, or PUT one record
    #
    #     behaviour:
    #
    #     * If Encounter exists as NEW, update
    #     * If Encounter exists as PROOFREAD, CURATED or PUBLISHED, skip and warn
    #     * If Encounter does not exists, create
    #
    #     The actual child model is looked up by "observation_name".
    #     """
    #     print("EncounterSerializer.save() called".format())
    #     # Keep observation_set in the fridge, make Encounter first
    #     obs_data = validated_data.pop("observation_set")

        # Extract Users from encounter: observer, reporter
        # o = validated_data.pop("observer")
        # observer, observer_created = User.objects.get_or_create(
        #     username=o["username"], email=o["email"])
        # print("observer {0} created {1}".format(observer, observer_created))
        #
        # o = validated_data.pop("reporter")
        # reporter, reporter_created = User.objects.get_or_create(
        #     username=o["username"], email=o["email"])

        # src = validated_data["source"]
        # srcid = validated_data["source_id"]
        #
        # if Encounter.objects.filter(source=src, source_id=srcid).exists():
        #     print("Encounter exists: {0}-{1}".format(src, srcid))
        #     encounter = Encounter.objects.get(source=src, source_id=srcid)
        #     if encounter.status == Encounter.STATUS_NEW:
        #         print("Encounter not proofread/curated, updating...")
        #         encounter.update(**validated_data)
        #         encounter.save()
        #     else:
        #         print("Encounter already changed, skipping.")
        # else:
        #     print("No Encounter with source/source_id found, creating new...")
        #     encounter = Encounter.objects.create(**validated_data)
        #     # encounter.reporter = reporter
        #     # encounter.observer = observer
        #     encounter.save()
        #
        #     for obs in obs_data:
        #         childmodel_name = obs.pop("observation_name")
        #         childmodel = getattr(Observation,
        #                              childmodel_name).related.related_model
        #         childmodel.objects.create(encounter=encounter, **obs)
        #
        # return encounter


class FastEncounterSerializer(GeoFeatureModelSerializer):
    """Encounter serializer.

    Alternative: serializers.HyperlinkedModelSerializer

    TODO: a writable version of the serializer will provide `create` and
    `update` methods, which also create/update the inline Observations.

    Since nested Observations are polymorphic, two steps have to be taken above
    the plain nested writeable API:

    * :mod:`wastd.observations.models.Observation.observation_name` is a property
      method to return the child model"s name
    * :mod:`wastd.api.ObservationSerializer` includes the `observation_name` in
      the API dict
    * :mod:`wastd.api.EncounterSerializer.create` and `update` (coming) handle
      both the Encounter and the nested Observations separately. Observations
      use their included `observation_name` to figure out the actual model that
      we want to `create` or `update`.

      TODO http://stackoverflow.com/q/32123148/2813717
      NOTE this API is not writeable, as related models (User and Observation)
      require customisations to handle data thrown at them.
    """

    # observation_set = ObservationSerializer(many=True, read_only=False)
    observer = FastUserSerializer(many=False, read_only=True)
    reporter = FastUserSerializer(many=False, read_only=True)
    area = FastAreaSerializer(many=False, read_only=True)
    site = FastAreaSerializer(many=False, read_only=True)
    survey = FastSurveySerializer(many=False, read_only=True)
    # observer = serializers.StringRelatedField(read_only=True)
    # reporter = serializers.StringRelatedField(read_only=True)
    # where = PointField(required=True)   ## THIS BREAKS GEOJSON OUTPUT
    leaflet_title = serializers.ReadOnlyField()
    latitude = serializers.ReadOnlyField()
    longitude = serializers.ReadOnlyField()
    crs = serializers.ReadOnlyField()
    absolute_admin_url = serializers.ReadOnlyField()
    photographs = MediaAttachmentSerializer(many=True, read_only=False)
    tx_logs = serializers.ReadOnlyField()

    class Meta:
        """Class options.

        The non-standard name `where` is declared as the geo field for the
        GeoJSON serializer"s benefit.
        """

        model = Encounter
        name = "encounter"
        fields = ("pk", "area", "site", "survey",
                  "where", "location_accuracy", "when",
                  "name", "observer", "reporter", "comments",
                  "status", "source", "source_id", "encounter_type",
                  "leaflet_title", "latitude", "longitude", "crs",
                  "absolute_admin_url", "photographs", "tx_logs",
                  #  "as_html", "as_latex",
                  # "observation_set",
                  )
        geo_field = "where"
        id_field = "source_id"


class AnimalEncounterSerializer(EncounterSerializer):
    """AnimalEncounter serializer."""

    photographs = MediaAttachmentSerializer(many=True, read_only=False)
    tx_logs = serializers.ReadOnlyField()

    class Meta:
        """Class options."""

        model = AnimalEncounter
        fields = ("pk", "area", "site", "survey", "source", "source_id",
                  "encounter_type", "leaflet_title",
                  "status", "observer", "reporter", "comments",
                  "where", "latitude", "longitude", "crs", "location_accuracy",
                  "when", "name",
                  "name", "taxon", "species", "health", "sex", "maturity", "behaviour",
                  "habitat", "activity", "nesting_event",
                  "checked_for_injuries",
                  "scanned_for_pit_tags",
                  "checked_for_flipper_tags",
                  "cause_of_death", "cause_of_death_confidence",
                  "absolute_admin_url", "photographs", "tx_logs",
                  "observation_set", )
        geo_field = "where"
        id_field = "source_id"


class TurtleNestEncounterSerializer(EncounterSerializer):
    """TurtleNestEncounter serializer."""

    class Meta:
        """Class options."""

        model = TurtleNestEncounter
        fields = ("pk", "area", "site", "survey", "source", "source_id",
                  "encounter_type", "leaflet_title",
                  "status", "observer", "reporter", "comments",
                  "where", "latitude", "longitude", "crs", "location_accuracy",
                  "when", "name",
                  "nest_age", "nest_type", "species", "habitat", "disturbance",
                  "comments",
                  "absolute_admin_url", "photographs", "tx_logs",
                  "observation_set",
                  )
        # read_only = ("photographs",)
        geo_field = "where"


class LoggerEncounterSerializer(EncounterSerializer):
    """LoggerEncounter serializer."""

    class Meta:
        """Class options."""

        model = LoggerEncounter
        fields = ("pk", "area", "site", "survey", "source", "source_id",
                  "encounter_type", "leaflet_title",
                  "status", "observer", "reporter", "comments",
                  "where", "latitude", "longitude", "crs", "location_accuracy",
                  "when", "name",
                  "deployment_status", "comments",
                  "comments",
                  "absolute_admin_url", "photographs", "tx_logs",
                  "observation_set", )
        geo_field = "where"


class EncounterFilter(filters.FilterSet):
    """Encounter filter."""

    when = rf_filters.DateFilter()

    class Meta:
        """Class opts."""

        model = Encounter
        fields = {
            "area": "__all__",
            "encounter_type": "__all__",
            "status": "__all__",
            "site": "__all__",
            "survey": "__all__",
            "source": "__all__",
            "location_accuracy": "__all__",
            "when": "__all__",
            "name": "__all__",
            "source_id": "__all__",
            "observer": "__all__",
            "reporter": "__all__",
            "comments": "__all__",
        }


class EncounterViewSet(viewsets.ModelViewSet):
    """Encounter view set.

    Encounters are a common, minimal, shared set of data about

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
    * [/api/1/encounters/?location_accuracy=10](/api/1/encounters/?location_accuracy=10) (captured as site name)
    * [/api/1/encounters/?location_accuracy=10000](/api/1/encounters/?location_accuracy=10000) (rough guess)

    # observer and reporter

    * [/api/1/encounters/?observer=100](/api/1/encounters/?observer=100) Observer with ID 100
    * [/api/1/encounters/?observer=100](/api/1/encounters/?reporter=100) Reporter with ID 100
    """

    latex_name = "latex/encounter.tex"
    queryset = Encounter.objects.all()
    serializer_class = EncounterSerializer
    search_fields = ("name", "source_id", )

    bbox_filter_field = "where"
    # bbox_filter_include_overlapping = True
    pagination_class = MyGeoJsonPagination
    filter_class = EncounterFilter

    def pre_latex(self, t_dir, data):
        """Symlink photographs to temp dir for use by latex template."""
        symlink_resources(t_dir, data)


class TurtleNestEncounterFilter(filters.FilterSet):
    """TurtleNestEncounter filter."""

    when = rf_filters.DateFilter()

    class Meta:
        """Class opts."""

        model = TurtleNestEncounter
        fields = {
            "area": "__all__",
            "encounter_type": "__all__",
            "status": "__all__",
            "site": "__all__",
            "survey": "__all__",
            "source": "__all__",
            "source_id": "__all__",
            "location_accuracy": "__all__",
            "when": "__all__",
            "name": "__all__",
            "observer": "__all__",
            "reporter": "__all__",
            "nest_age": "__all__",
            "nest_type": "__all__",
            "species": "__all__",
            "habitat": "__all__",
            "disturbance": "__all__",
            "comments": "__all__",
        }


class TurtleNestEncounterViewSet(viewsets.ModelViewSet):
    """TurtleNestEncounter view set.

    TNE are turtle tracks with or without nests.

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
    """

    latex_name = "latex/turtlenestencounter.tex"
    queryset = TurtleNestEncounter.objects.all()
    serializer_class = TurtleNestEncounterSerializer
    filter_class = TurtleNestEncounterFilter
    pagination_class = MyGeoJsonPagination

    def pre_latex(self, t_dir, data):
        """Symlink photographs to temp dir for use by latex template."""
        symlink_resources(t_dir, data)


class AnimalEncounterFilter(filters.FilterSet):
    """TurtleNestEncounter filter."""

    when = rf_filters.DateFilter()

    class Meta:
        """Class opts."""

        model = AnimalEncounter
        fields = {
            "encounter_type": "__all__",
            "status": "__all__",
            "area": "__all__",
            "site": "__all__",
            "survey": "__all__",
            "source": "__all__",
            "source_id": "__all__",
            "location_accuracy": "__all__",
            "when": "__all__",
            "name": "__all__",
            "observer": "__all__",
            "reporter": "__all__",
            "taxon": "__all__",
            "species": "__all__",
            "health": "__all__",
            "sex": "__all__",
            "maturity": "__all__",
            "habitat": "__all__",
            "checked_for_injuries": "__all__",
            "scanned_for_pit_tags": "__all__",
            "checked_for_flipper_tags": "__all__",
            "cause_of_death": "__all__",
            "cause_of_death_confidence": "__all__",
        }


class AnimalEncounterViewSet(viewsets.ModelViewSet):
    """AnimalEncounter view set.

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

    "health", "sex", "maturity", "checked_for_injuries", "scanned_for_pit_tags", "checked_for_flipper_tags",
    "cause_of_death", "cause_of_death_confidence"

    # habitat
    * [/api/1/turtle-nest-encounters/?habitat=na](/api/1/turtle-nest-encounters/?habitat=na) unknown habitat
    * [/api/1/turtle-nest-encounters/?habitat=beach-below-high-water](
      /api/1/turtle-nest-encounters/?habitat=beach-below-high-water) beach below high water mark
    * [/api/1/turtle-nest-encounters/?habitat=beach-above-high-water](
      /api/1/turtle-nest-encounters/?habitat=beach-above-high-water) beach above high water mark and dune
    * [/api/1/turtle-nest-encounters/?habitat=beach-edge-of-vegetation](
      /api/1/turtle-nest-encounters/?habitat=beach-edge-of-vegetation) edge of vegetation
    * [/api/1/turtle-nest-encounters/?habitat=in-dune-vegetation](
      /api/1/turtle-nest-encounters/?habitat=in-dune-vegetation) inside vegetation
    * plus all other habitat choices.

    """

    latex_name = "latex/animalencounter.tex"
    queryset = AnimalEncounter.objects.all()
    serializer_class = AnimalEncounterSerializer
    filter_class = AnimalEncounterFilter
    search_fields = ("name", "source_id", "behaviour", )
    pagination_class = MyGeoJsonPagination
    # filter_backends = (CustomBBoxFilter, filters.DjangoFilterBackend, )

    def pre_latex(self, t_dir, data):
        """Symlink photographs to temp dir for use by latex template."""
        symlink_resources(t_dir, data)


class LoggerEncounterViewSet(viewsets.ModelViewSet):
    """LoggerEncounter view set."""

    latex_name = "latex/loggerencounter.tex"
    queryset = LoggerEncounter.objects.all()
    serializer_class = LoggerEncounterSerializer
    filter_fields = ["encounter_type",
                     "status", "area", "site", "survey", "source", "source_id",
                     "location_accuracy", "when", "name", "observer", "reporter",
                     "deployment_status", "comments"]
    search_fields = ("name", "source_id", )
    pagination_class = MyGeoJsonPagination

    def pre_latex(self, t_dir, data):
        """Symlink photographs to temp dir for use by latex template."""
        symlink_resources(t_dir, data)


class ObservationViewSet(viewsets.ModelViewSet):
    """Observation view set."""

    queryset = Observation.objects.all()
    serializer_class = ObservationSerializer


class MediaAttachmentViewSet(viewsets.ModelViewSet):
    """MediaAttachment view set."""

    queryset = MediaAttachment.objects.all()
    serializer_class = MediaAttachmentSerializer
    pagination_class = MyGeoJsonPagination


# ----------------------------------------------------------------------------#
# TagObservation
# ----------------------------------------------------------------------------#
class TagObservationSerializer(serializers.ModelSerializer):
    """TagObservation serializer."""

    # as_latex = serializers.ReadOnlyField()

    class Meta:
        """Class options."""

        model = TagObservation
        fields = ("observation_name",  # "as_latex",
                  "tag_type", "name", "tag_location",
                  "status", "comments", )


class TagObservationEncounterSerializer(GeoFeatureModelSerializer):
    """TagObservation serializer including encounter for standalone viewset."""

    encounter = FastEncounterSerializer(many=False, read_only=True)
    point = GeometryField()

    class Meta:
        """Class options."""

        model = TagObservation
        geo_field = "point"
        fields = ("encounter", "observation_name", "tag_type", "name",
                  "tag_location", "status", "comments", )


class TagObservationViewSet(viewsets.ModelViewSet):
    """TagObservation view set."""

    queryset = TagObservation.objects.all()
    serializer_class = TagObservationEncounterSerializer
    filter_fields = ["encounter__area", "encounter__site", "encounter__encounter_type",
                     "tag_type", "tag_location", "name", "status", "comments"]
    search_fields = ("name", "comments", )
    pagination_class = MyGeoJsonPagination


# ----------------------------------------------------------------------------#
# TurtleNestObservation
# ----------------------------------------------------------------------------#
class TurtleMorphometricObservationSerializer(serializers.ModelSerializer):
    """TurtleMorphometricObservation serializer."""

    # as_latex = serializers.ReadOnlyField()

    class Meta:
        """Class options."""

        model = TurtleMorphometricObservation
        fields = ("observation_name",  # "as_latex",
                  "curved_carapace_length_mm", "curved_carapace_length_accuracy",
                  "straight_carapace_length_mm", "straight_carapace_length_accuracy",
                  "curved_carapace_width_mm", "curved_carapace_width_accuracy",
                  "tail_length_carapace_mm", "tail_length_carapace_accuracy",
                  "tail_length_vent_mm", "tail_length_vent_accuracy",
                  "tail_length_plastron_mm", "tail_length_plastron_accuracy",
                  "maximum_head_width_mm", "maximum_head_width_accuracy",
                  "maximum_head_length_mm", "maximum_head_length_accuracy",
                  "body_depth_mm", "body_depth_accuracy",
                  "body_weight_g", "body_weight_accuracy",
                  "handler", "recorder", )


class TurtleMorphometricObservationEncounterSerializer(GeoFeatureModelSerializer):
    """TurtleMorphometricObservation serializer including encounter for standalone viewset."""

    encounter = FastEncounterSerializer(many=False, read_only=True)
    point = GeometryField()

    class Meta:
        """Class options."""

        model = TurtleMorphometricObservation
        geo_field = "point"
        fields = (
            "encounter", "observation_name", "latitude", "longitude",
            "curved_carapace_length_mm", "curved_carapace_length_accuracy",
            "straight_carapace_length_mm", "straight_carapace_length_accuracy",
            "curved_carapace_width_mm", "curved_carapace_width_accuracy",
            "tail_length_carapace_mm", "tail_length_carapace_accuracy",
            "tail_length_vent_mm", "tail_length_vent_accuracy",
            "tail_length_plastron_mm", "tail_length_plastron_accuracy",
            "maximum_head_width_mm", "maximum_head_width_accuracy",
            "maximum_head_length_mm", "maximum_head_length_accuracy",
            "body_depth_mm", "body_depth_accuracy",
            "body_weight_g", "body_weight_accuracy",
            "handler", "recorder",
        )


class TurtleMorphometricObservationViewSet(viewsets.ModelViewSet):
    """TurtleNestObservation view set."""

    queryset = TurtleMorphometricObservation.objects.all()
    serializer_class = TurtleMorphometricObservationEncounterSerializer
    filter_fields = ["encounter__area", "encounter__site", "encounter__encounter_type",
                     "encounter__status"]
    search_fields = ("comments", )
    pagination_class = MyGeoJsonPagination

# ----------------------------------------------------------------------------#
# TurtleNestObservation
# ----------------------------------------------------------------------------#


class TurtleNestObservationSerializer(serializers.ModelSerializer):
    """TurtleNestObservation serializer."""

    # as_latex = serializers.ReadOnlyField()

    class Meta:
        """Class options."""

        model = TurtleNestObservation
        fields = ("observation_name",  # "as_latex",
                  "nest_position", "eggs_laid", "egg_count",
                  "egg_count_calculated",
                  "no_emerged", "no_egg_shells",
                  "no_live_hatchlings_neck_of_nest",
                  "no_live_hatchlings", "no_dead_hatchlings",
                  "no_undeveloped_eggs", "no_unhatched_eggs",
                  "no_unhatched_term", "no_depredated_eggs",
                  "nest_depth_top", "nest_depth_bottom",
                  "sand_temp", "air_temp", "water_temp", "egg_temp",
                  "hatching_success", "emergence_success",
                  "comments")


class TurtleNestObservationEncounterSerializer(GeoFeatureModelSerializer):
    """TurtleNestObservation serializer including encounter for standalone viewset."""

    encounter = FastEncounterSerializer(many=False, read_only=True)
    point = GeometryField()

    class Meta:
        """Class options."""

        model = TurtleNestObservation
        geo_field = "point"
        fields = (
            "encounter", "observation_name", "latitude", "longitude",
            "nest_position", "eggs_laid", "egg_count",
            "hatching_success", "emergence_success",
            "no_egg_shells", "no_live_hatchlings_neck_of_nest", "no_live_hatchlings",
            "no_dead_hatchlings", "no_undeveloped_eggs",
            "no_unhatched_eggs", "no_unhatched_term", "no_depredated_eggs",
            "nest_depth_top", "nest_depth_bottom",
            "sand_temp", "air_temp", "water_temp", "egg_temp", "comments",
        )


class TurtleNestObservationViewSet(viewsets.ModelViewSet):
    """TurtleNestObservation view set."""

    queryset = TurtleNestObservation.objects.all()
    serializer_class = TurtleNestObservationEncounterSerializer
    filter_fields = ["encounter__area", "encounter__site", "encounter__encounter_type",
                     "nest_position", "eggs_laid", "encounter__status"]
    search_fields = ("comments", )
    pagination_class = MyGeoJsonPagination


# ----------------------------------------------------------------------------#
# NestTagObservation
# ----------------------------------------------------------------------------#
class NestTagObservationSerializer(serializers.ModelSerializer):
    """NestTagObservationSerializer."""

    # as_latex = serializers.ReadOnlyField()

    class Meta:
        """Class options."""

        model = NestTagObservation
        fields = ("observation_name",  # "as_latex", #
                  "status",
                  "flipper_tag_id",
                  "date_nest_laid",
                  "tag_label",
                  "comments",
                  )


class NestTagObservationEncounterSerializer(GeoFeatureModelSerializer):
    """NestTagObservationSerializer with encounter."""

    encounter = FastEncounterSerializer(many=False, read_only=True)
    point = GeometryField()

    class Meta:
        """Class options."""

        model = NestTagObservation
        geo_field = "point"
        fields = (
            "encounter",
            "observation_name",
            "status",
            "flipper_tag_id",
            "date_nest_laid",
            "tag_label",
            "comments",)


class NestTagObservationViewSet(viewsets.ModelViewSet):
    """NestTagObservation view set."""

    queryset = NestTagObservation.objects.all()
    serializer_class = NestTagObservationEncounterSerializer
    filter_fields = ["encounter__area", "encounter__site", "encounter__encounter_type",
                     "status", "flipper_tag_id", "date_nest_laid", "tag_label", "comments"]
    # pagination_class = pagination.LimitOffsetPagination
    pagination_class = MyGeoJsonPagination


# ----------------------------------------------------------------------------#
# TurtleNestDisturbanceObservation
# ----------------------------------------------------------------------------#
class TurtleNestDisturbanceObservationSerializer(serializers.ModelSerializer):
    """TurtleNestDisturbanceObservation serializer."""

    # as_latex = serializers.ReadOnlyField()

    class Meta:
        """Class options."""

        model = TurtleNestDisturbanceObservation
        fields = ("observation_name",  # "as_latex",
                  "disturbance_cause", "disturbance_cause_confidence",
                  "disturbance_severity", "comments", )


class TurtleNestDisturbanceObservationEncounterSerializer(GeoFeatureModelSerializer):
    """TurtleNestDisturbanceObservation serializer with encounter."""

    encounter = FastEncounterSerializer(many=False, read_only=True)
    point = GeometryField()

    class Meta:
        """Class options."""

        model = TurtleNestDisturbanceObservation
        geo_field = "point"
        fields = (
            "encounter",
            "observation_name",
            "disturbance_cause",
            "disturbance_cause_confidence",
            "disturbance_severity",
            "comments", )


class TurtleNestDisturbanceObservationEncounterViewSet(viewsets.ModelViewSet):
    """TurtleNestDisturbanceObservation view set."""

    queryset = TurtleNestDisturbanceObservation.objects.all()
    serializer_class = TurtleNestDisturbanceObservationEncounterSerializer
    filter_fields = ["encounter__area", "encounter__site", "encounter__encounter_type",
                     "disturbance_cause", "disturbance_cause_confidence", "disturbance_severity", ]
    # pagination_class = pagination.LimitOffsetPagination
    pagination_class = MyGeoJsonPagination


# ----------------------------------------------------------------------------#
# HatchlingMorphometricObservation
# ----------------------------------------------------------------------------#

class HatchlingMorphometricObservationSerializer(serializers.ModelSerializer):
    """HatchlingMorphometricObservationSerializer."""

    # as_latex = serializers.ReadOnlyField()

    class Meta:
        """Class options."""

        model = HatchlingMorphometricObservation
        fields = ("observation_name",  # "as_latex", #
                  "straight_carapace_length_mm",
                  "straight_carapace_width_mm",
                  "body_weight_g",
                  )


class HatchlingMorphometricObservationEncounterSerializer(GeoFeatureModelSerializer):
    """HatchlingMorphometricObservation serializer including encounter for standalone viewset."""
    encounter = FastEncounterSerializer(many=False, read_only=True)
    point = GeometryField()

    class Meta:
        """Class options."""

        model = HatchlingMorphometricObservation
        geo_field = "point"
        fields = (
            # From Encounter:
            "encounter",
            "observation_name",
            "latitude",
            "longitude",
            # From model:
            "straight_carapace_length_mm",
            "straight_carapace_width_mm",
            "body_weight_g",
        )


class HatchlingMorphometricObservationEncounterViewSet(viewsets.ModelViewSet):
    """HatchlingMorphometricObservation view set."""

    queryset = HatchlingMorphometricObservation.objects.all()
    serializer_class = HatchlingMorphometricObservationEncounterSerializer
    filter_fields = ["encounter__area", "encounter__site", "encounter__encounter_type", ]
    # pagination_class = pagination.LimitOffsetPagination
    pagination_class = MyGeoJsonPagination

# ----------------------------------------------------------------------------#
# TurtleHatchlingEmergenceObservation
# ----------------------------------------------------------------------------#


class TurtleHatchlingEmergenceObservationSerializer(serializers.ModelSerializer):
    """TurtleHatchlingEmergenceObservation serializer excluding encounter for inlines."""

    class Meta:
        """Class options."""

        model = TurtleHatchlingEmergenceObservation
        fields = (
            "bearing_to_water_degrees",
            "bearing_leftmost_track_degrees",
            "bearing_rightmost_track_degrees",
            "no_tracks_main_group",
            "no_tracks_main_group_min",
            "no_tracks_main_group_max",
            "outlier_tracks_present",
            "path_to_sea_comments",
            "hatchling_emergence_time_known",
            "light_sources_present",
            "hatchling_emergence_time",
            "hatchling_emergence_time_accuracy",
            "cloud_cover_at_emergence",
        )


class TurtleHatchlingEmergenceObservationEncounterSerializer(GeoFeatureModelSerializer):
    """TurtleHatchlingEmergenceObservation serializer including encounter for standalone viewset."""
    encounter = FastEncounterSerializer(many=False, read_only=True)
    point = GeometryField()

    class Meta:
        """Class options."""

        model = TurtleHatchlingEmergenceObservation
        geo_field = "point"
        fields = (
            # From Encounter:
            "encounter",
            "observation_name",
            "latitude",
            "longitude",
            # From model:
            "bearing_to_water_degrees",
            "bearing_leftmost_track_degrees",
            "bearing_rightmost_track_degrees",
            "no_tracks_main_group",
            "no_tracks_main_group_min",
            "no_tracks_main_group_max",
            "outlier_tracks_present",
            "path_to_sea_comments",
            "hatchling_emergence_time_known",
            "light_sources_present",
            "hatchling_emergence_time",
            "hatchling_emergence_time_accuracy",
            "cloud_cover_at_emergence",
        )


class TurtleHatchlingEmergenceObservationEncounterViewSet(viewsets.ModelViewSet):
    """TurtleHatchlingEmergenceObservation view set."""

    queryset = TurtleHatchlingEmergenceObservation.objects.all()
    serializer_class = TurtleHatchlingEmergenceObservationEncounterSerializer
    filter_fields = ["encounter__area", "encounter__site", "encounter__encounter_type", ]
    # pagination_class = pagination.LimitOffsetPagination
    pagination_class = MyGeoJsonPagination


# ----------------------------------------------------------------------------#
# TurtleHatchlingEmergenceOutlierObservation
# ----------------------------------------------------------------------------#
class TurtleHatchlingEmergenceOutlierObservationSerializer(serializers.ModelSerializer):
    """TurtleHatchlingEmergenceOutlierObservation serializer excluding encounter for inlines."""

    class Meta:
        """Class options."""

        model = TurtleHatchlingEmergenceOutlierObservation

        fields = (
            "bearing_outlier_track_degrees",
            "outlier_group_size",
            "outlier_track_comment",
        )


class TurtleHatchlingEmergenceOutlierObservationEncounterSerializer(GeoFeatureModelSerializer):
    """TurtleHatchlingEmergenceOutlierObservation serializer including encounter for standalone viewset."""
    encounter = FastEncounterSerializer(many=False, read_only=True)
    point = GeometryField()

    class Meta:
        """Class options."""

        model = TurtleHatchlingEmergenceOutlierObservation
        geo_field = "point"
        fields = (
            # From Encounter:
            "encounter",
            "observation_name",
            "latitude",
            "longitude",
            # From model:
            "bearing_outlier_track_degrees",
            "outlier_group_size",
            "outlier_track_comment",

        )


class TurtleHatchlingEmergenceOutlierObservationEncounterViewSet(viewsets.ModelViewSet):
    """TurtleHatchlingEmergenceOutlierObservation view set."""

    queryset = TurtleHatchlingEmergenceOutlierObservation.objects.all()
    serializer_class = TurtleHatchlingEmergenceOutlierObservationEncounterSerializer
    filter_fields = ["encounter__area", "encounter__site", "encounter__encounter_type", ]
    # pagination_class = pagination.LimitOffsetPagination
    pagination_class = MyGeoJsonPagination


# ----------------------------------------------------------------------------#
# LightSourceObservation
# ----------------------------------------------------------------------------#
class LightSourceObservationSerializer(serializers.ModelSerializer):
    """LightSource serializer excluding encounter for inlines."""

    class Meta:
        """Class options."""

        model = LightSourceObservation
        fields = (
            "bearing_light_degrees",
            "light_source_type",
            "light_source_description",
        )


class LightSourceObservationEncounterSerializer(GeoFeatureModelSerializer):
    """LightSource serializer including encounter for standalone viewsets."""
    encounter = FastEncounterSerializer(many=False, read_only=True)
    point = GeometryField()

    class Meta:
        """Class options."""

        model = LightSourceObservation
        geo_field = "point"
        fields = (
            # From Encounter:
            "encounter",
            "observation_name",
            "latitude",
            "longitude",
            # From model:
            "bearing_light_degrees",
            "light_source_type",
            "light_source_description",
        )


class LightSourceObservationEncounterViewSet(viewsets.ModelViewSet):
    """LightSourceObservation view set."""

    queryset = LightSourceObservation.objects.all()
    serializer_class = LightSourceObservationEncounterSerializer
    filter_fields = ["encounter__area", "encounter__site", "encounter__encounter_type", ]
    # pagination_class = pagination.LimitOffsetPagination
    pagination_class = MyGeoJsonPagination


# ----------------------------------------------------------------------------#

# Encounters
router.register(r"encounters", EncounterViewSet)
router.register(r"animal-encounters", AnimalEncounterViewSet)
router.register(r"turtle-nest-encounters", TurtleNestEncounterViewSet)
router.register(r"logger-encounters", LoggerEncounterViewSet)

# Observations
router.register(r"observations", ObservationViewSet)
router.register(r"media-attachments", MediaAttachmentViewSet)
router.register(r"tag-observations", TagObservationViewSet)

router.register(r"turtle-morphometrics", TurtleMorphometricObservationViewSet)

router.register(r"turtle-nest-tag-observations", NestTagObservationViewSet)
router.register(r"turtle-nest-disturbance-observations", TurtleNestDisturbanceObservationEncounterViewSet)
router.register(r"turtle-nest-excavations", TurtleNestObservationViewSet)
router.register(r"turtle-nest-hatchling-morphometrics", HatchlingMorphometricObservationEncounterViewSet)
router.register(r"turtle-nest-hatchling-emergences", TurtleHatchlingEmergenceObservationEncounterViewSet)
router.register(r"turtle-nest-hatchling-emergence-outliers", TurtleHatchlingEmergenceOutlierObservationEncounterViewSet)
router.register(r"turtle-nest-hatchling-emergence-light-sources", LightSourceObservationEncounterViewSet)


# Taxonomy: Serializers -------------------------------------------------------------------#


class HbvNameSerializer(serializers.ModelSerializer):
    """Serializer for HBVName."""

    class Meta:
        """Opts."""

        model = HbvName
        fields = "__all__"


class HbvSupraSerializer(serializers.ModelSerializer):
    """Serializer for HbvSupra."""

    class Meta:
        """Opts."""

        model = HbvSupra
        fields = "__all__"


class HbvGroupSerializer(serializers.ModelSerializer):
    """Serializer for HbvGroup."""

    class Meta:
        """Opts."""

        model = HbvGroup
        fields = "__all__"


class HbvFamilySerializer(serializers.ModelSerializer):
    """Serializer for HbvFamily."""

    class Meta:
        """Opts."""

        model = HbvFamily
        fields = "__all__"


class HbvGenusSerializer(serializers.ModelSerializer):
    """Serializer for HbvGenus."""

    class Meta:
        """Opts."""

        model = HbvGenus
        fields = "__all__"


class HbvSpeciesSerializer(serializers.ModelSerializer):
    """Serializer for HbvSpecies."""

    class Meta:
        """Opts."""

        model = HbvSpecies
        fields = "__all__"


class HbvVernacularSerializer(serializers.ModelSerializer):
    """Serializer for HbvVernacular."""

    class Meta:
        """Opts."""

        model = HbvVernacular
        fields = "__all__"


class HbvXrefSerializer(serializers.ModelSerializer):
    """Serializer for HbvXref."""

    class Meta:
        """Opts."""

        model = HbvXref
        fields = "__all__"


class HbvParentSerializer(serializers.ModelSerializer):
    """Serializer for HbvParent."""

    class Meta:
        """Opts."""

        model = HbvParent
        fields = "__all__"

# Taxonomy: Filters -------------------------------------------------------------------#


class HbvNameFilter(filters.FilterSet):
    """HbvName filter."""

    class Meta:
        """Class opts."""

        model = HbvName
        fields = {
            "rank_name": "__all__",
            "is_current": "__all__",
            "naturalised_status": "__all__",
            "naturalised_certainty": "__all__",
            "is_eradicated": "__all__",
            "informal": "__all__",
            "name": "__all__",
            "name_id": "__all__",
            "full_name": "__all__",
            "vernacular": "__all__",
            "all_vernaculars": "__all__",
            "author": "__all__",
            "ogc_fid": "__all__",
            "name_id": "__all__",
            "kingdom_id": "__all__",
            "rank_id": "__all__",
            "rank_name": "__all__",
            "name1": "__all__",
            "name2": "__all__",
            "rank3": "__all__",
            "name3": "__all__",
            "rank4": "__all__",
            "name4": "__all__",
            "pub_id": "__all__",
            "vol_info": "__all__",
            "pub_year": "__all__",
            "is_current": "__all__",
            "origin": "__all__",
            "naturalised_status": "__all__",
            "naturalised_certainty": "__all__",
            "is_eradicated": "__all__",
            "naturalised_comments": "__all__",
            "informal": "__all__",
            "form_desc_yr": "__all__",
            "form_desc_mn": "__all__",
            "form_desc_dy": "__all__",
            "comments": "__all__",
            "added_by": "__all__",
            "added_on": "__all__",
            "updated_by": "__all__",
            "updated_on": "__all__",
            "family_code": "__all__",
            "family_nid": "__all__",
            "name": "__all__",
            "full_name": "__all__",
            "author": "__all__",
            "reference": "__all__",
            "editor": "__all__",
            "vernacular": "__all__",
            "all_vernaculars": "__all__",
            "linear_sequence": "__all__",
            "md5_rowhash": "__all__",
        }


class HbvSupraFilter(filters.FilterSet):
    """HbvSupra filter."""

    class Meta:
        """Class opts."""

        model = HbvSupra
        fields = {
            "ogc_fid": "__all__",
            "supra_code": "__all__",
            "supra_name": "__all__",
            "updated_on": "__all__",
            "md5_rowhash": "__all__",
        }


class HbvGroupFilter(filters.FilterSet):
    """HbvGroup filter."""

    class Meta:
        """Class opts."""

        model = HbvGroup
        fields = {
            "ogc_fid": "__all__",
            "class_id": "__all__",
            "name_id": "__all__",
            "updated_by": "__all__",
            "updated_on": "__all__",
            "rank_name": "__all__",
            "name": "__all__",
            "md5_rowhash": "__all__",
        }


class HbvFamilyFilter(filters.FilterSet):
    """HbvFamily filter."""

    class Meta:
        """Class opts."""

        model = HbvFamily
        fields = {
            "ogc_fid": "__all__",
            "name_id": "__all__",
            "kingdom_id": "__all__",
            "rank_id": "__all__",
            "rank_name": "__all__",
            "family_name": "__all__",
            "is_current": "__all__",
            "informal": "__all__",
            "comments": "__all__",
            "family_code": "__all__",
            "linear_sequence": "__all__",
            "order_nid": "__all__",
            "order_name": "__all__",
            "class_nid": "__all__",
            "class_name": "__all__",
            "division_nid": "__all__",
            "division_name": "__all__",
            "kingdom_name": "__all__",
            "author": "__all__",
            "editor": "__all__",
            "reference": "__all__",
            "supra_code": "__all__",
            "added_on": "__all__",
            "updated_on": "__all__",
            "md5_rowhash": "__all__",
        }


class HbvGenusFilter(filters.FilterSet):
    """HbvGenus filter."""

    class Meta:
        """Class opts."""

        model = HbvGenus
        fields = {
            "ogc_fid": "__all__",
            "name_id": "__all__",
            "kingdom_id": "__all__",
            "rank_id": "__all__",
            "rank_name": "__all__",
            "genus": "__all__",
            "is_current": "__all__",
            "informal": "__all__",
            "comments": "__all__",
            "family_code": "__all__",
            "family_nid": "__all__",
            "author": "__all__",
            "editor": "__all__",
            "reference": "__all__",
            "genusid": "__all__",
            "added_on": "__all__",
            "updated_on": "__all__",
            "md5_rowhash": "__all__",
        }


class HbvSpeciesFilter(filters.FilterSet):
    """HbvSpecies filter."""

    class Meta:
        """Class opts."""

        model = HbvSpecies
        fields = {
            "ogc_fid": "__all__",
            "name_id": "__all__",
            "kingdom_id": "__all__",
            "rank_id": "__all__",
            "rank_name": "__all__",
            "family_code": "__all__",
            "family_nid": "__all__",
            "genus": "__all__",
            "species": "__all__",
            "infra_rank": "__all__",
            "infra_name": "__all__",
            "infra_rank2": "__all__",
            "infra_name2": "__all__",
            "author": "__all__",
            "editor": "__all__",
            "reference": "__all__",
            "comments": "__all__",
            "vernacular": "__all__",
            "all_vernaculars": "__all__",
            "species_name": "__all__",
            "species_code": "__all__",
            "is_current": "__all__",
            "naturalised": "__all__",
            "naturalised_status": "__all__",
            "naturalised_certainty": "__all__",
            "is_eradicated": "__all__",
            "naturalised_comments": "__all__",
            "informal": "__all__",
            "added_on": "__all__",
            "updated_on": "__all__",
            "consv_code": "__all__",
            "md5_rowhash": "__all__",
        }


class HbvVernacularFilter(filters.FilterSet):
    """HbvVernacular filter."""

    class Meta:
        """Class opts."""

        model = HbvVernacular
        fields = {
            "ogc_fid": "__all__",
            "name_id": "__all__",
            "name": "__all__",
            "vernacular": "__all__",
            "language": "__all__",
            "lang_pref": "__all__",
            "preferred": "__all__",
            "source": "__all__",
            "updated_by": "__all__",
            "updated_on": "__all__",
            "md5_rowhash": "__all__",
        }


class HbvXrefFilter(filters.FilterSet):
    """HbvXref filter."""

    class Meta:
        """Class opts."""

        model = HbvXref
        fields = {
            "ogc_fid": "__all__",
            "xref_id": "__all__",
            "old_name_id": "__all__",
            "new_name_id": "__all__",
            "xref_type": "__all__",
            "active": "__all__",
            "authorised_by": "__all__",
            "authorised_on": "__all__",
            "comments": "__all__",
            "added_on": "__all__",
            "updated_on": "__all__",
            "md5_rowhash": "__all__",
        }


class HbvParentFilter(filters.FilterSet):
    """HbvParent filter."""

    class Meta:
        """Class opts."""

        model = HbvParent
        fields = {
            "ogc_fid": "__all__",
            "name_id": "__all__",
            "class_id": "__all__",
            "parent_nid": "__all__",
            "updated_by": "__all__",
            "updated_on": "__all__",
            "md5_rowhash": "__all__",
        }


# Taxonomy: Viewsets ---------------------------------------------------------#
class HbvNameViewSet(NameIDBatchUpsertViewSet):
    """View set for HbvName.

    # Custom features
    POST a GeoJSON feature properties dict to create or update the corresponding Taxon.

    # Pagination: LimitOffset
    The results have four top-level keys:

    * `count` Total number of features
    * `next` URL to next batch. `null` in last page.
    * `previous` URL to previous batch. `null` in first page.

    You can subset your own page with GET parameters `limit` and `offset`, e.g.
    [/api/1/taxonomy/?limit=100&offset=100](/api/1/taxonomy/?limit=100&offset=100).

    # Search and filter

    The following fields offer search filters `exact`, `iexact`, `in`, `startswith`,
    `istartswith`, `contains`, `icontains`:

    `rank_name`,  `is_current`, `naturalised_status`, ` naturalised_certainty`,
    `is_eradicated`, `informal`, `name`, `name_id`, `full_name`, `vernacular`, `all_vernaculars`, `author`.

    Learn more about filter usage at
    [django-rest-framework-filters](https://github.com/philipn/django-rest-framework-filters).

    # Search names
    Search `name`, `name_id`, `full_name`, `vernacular`, `all_vernaculars`, `author` as follows:

    * [/api/1/taxonomy/?full_name__icontains=acacia](/api/1/taxonomy/?full_name__icontains=acacia)
      Any taxon with case-insensitive phrase "acacia" in field `full_name`.
    * Substitute `full_name` for any of name, full_name, vernacular, all_vernaculars, author.
    * Substitute icontains for any of `exact`, `iexact`, `in`, `startswith`, `istartswith`, `contains`.

    # Taxonomic rank

    * [/api/1/taxonomy/?rank_name=Kingdom](/api/1/taxonomy/?rank_name=Kingdom)
      Taxa of exact, case-sensitive rank_name "Kingdom".
    * [/api/1/taxonomy/?rank_name__startswith=King](/api/1/taxonomy/?rank_name__startswith=King)
      Taxa of rank_names starting with the exact, case-sensitive phrase "King".
    * Other ranks available: Division, Phylum, Class, Subclass, Order, Family, Subfamily,
      Genus, Species, Subspecies, Variety, Form

    # Current
    Whether the taxon is current or not:

    * [/api/1/taxonomy/?is_current=Y](/api/1/taxonomy/?is_current=Y) Only current names
    * [/api/1/taxonomy/?is_current=N](/api/1/taxonomy/?is_current=N) Only non-current names

    # Name approval status
    Whether the name is a phrase name, manuscript name, or approved:

    * [/api/1/taxonomy/?informal=PN](/api/1/taxonomy/?informal=PN) Phrase Name
    * [/api/1/taxonomy/?informal=MS](/api/1/taxonomy/?informal=MS) Manuscript Name
    * [/api/1/taxonomy/?informal=-](/api/1/taxonomy/?informal=-) Approved Name

    # Naturalised
    Whether the taxon is naturalised in WA:

    * [/api/1/taxonomy/?naturalised_status=A](/api/1/taxonomy/?naturalised_status=A) A
    * [/api/1/taxonomy/?naturalised_status=M](/api/1/taxonomy/?naturalised_status=M) M
    * [/api/1/taxonomy/?naturalised_status=N](/api/1/taxonomy/?naturalised_status=N) N
    * [/api/1/taxonomy/?naturalised_status=-](/api/1/taxonomy/?naturalised_status=-) -

    # Naturalised certainty
    * [/api/1/taxonomy/?naturalised_certainty=N](/api/1/taxonomy/?naturalised_certainty=N) N
    * [/api/1/taxonomy/?naturalised_certainty=Y](/api/1/taxonomy/?naturalised_certainty=Y) Y
    * [/api/1/taxonomy/?naturalised_certainty=-](/api/1/taxonomy/?naturalised_certainty=-) -

    # Eradicated
    * [/api/1/taxonomy/?is_eradicated=Y](/api/1/taxonomy/?is_eradicated=Y) Y
    * [/api/1/taxonomy/?is_eradicated=-](/api/1/taxonomy/?is_eradicated=-) -
    """

    queryset = HbvName.objects.all()
    serializer_class = HbvNameSerializer
    filter_class = HbvNameFilter
    model = HbvName
    uid_fields = ("name_id",)


router.register("names", HbvNameViewSet)


class HbvSupraViewSet(BatchUpsertViewSet):
    """View set for HbvSupra. See HBV Names for details and usage examples."""

    queryset = HbvSupra.objects.all()
    serializer_class = HbvSupraSerializer
    filter_class = HbvSupraFilter
    model = HbvSupra
    uid_fields = ("supra_code", )

    def fetch_existing_records(self, new_records, model):
        """Fetch pk, (status if QC mixin), and **uid_fields values from a model."""

        qs = model.objects.filter(
            supra_code__in=list(set([x["supra_code"] for x in new_records]))
        )

        # if issubclass(model, QualityControlMixin):
        #     return qs.values("pk", "supra_code", "status")
        # else:
        return qs.values("pk", "supra_code", )


router.register("supra", HbvSupraViewSet)


class HbvGroupViewSet(NameIDBatchUpsertViewSet):
    """View set for HbvGroup.See HBV Names for details and usage examples."""

    queryset = HbvGroup.objects.all()
    serializer_class = HbvGroupSerializer
    filter_class = HbvGroupFilter
    model = HbvGroup
    uid_fields = ("name_id",)


router.register("groups", HbvGroupViewSet)


class HbvFamilyViewSet(NameIDBatchUpsertViewSet):
    """View set for HbvFamily. See HBV Names for details and usage examples."""

    queryset = HbvFamily.objects.all()
    serializer_class = HbvFamilySerializer
    filter_class = HbvFamilyFilter
    model = HbvFamily
    uid_fields = ("name_id",)


router.register("families", HbvFamilyViewSet)


class HbvGenusViewSet(NameIDBatchUpsertViewSet):
    """View set for HbvGenus. See HBV Names for details and usage examples."""

    queryset = HbvGenus.objects.all()
    serializer_class = HbvGenusSerializer
    filter_class = HbvGenusFilter
    model = HbvGenus
    uid_fields = ("name_id",)


router.register("genera", HbvGenusViewSet)


class HbvSpeciesViewSet(NameIDBatchUpsertViewSet):
    """View set for HbvSpecies. See HBV Names for details and usage examples."""

    queryset = HbvSpecies.objects.all()
    serializer_class = HbvSpeciesSerializer
    filter_class = HbvSpeciesFilter
    model = HbvSpecies
    uid_fields = ("name_id",)


router.register("species", HbvSpeciesViewSet)


class HbvVernacularViewSet(OgcFidBatchUpsertViewSet):
    """View set for HbvVernacular. See HBV Names for details and usage examples."""

    queryset = HbvVernacular.objects.all()
    serializer_class = HbvVernacularSerializer
    filter_class = HbvVernacularFilter
    model = HbvVernacular
    uid_fields = ("ogc_fid", )

    # def create_one(self, data):
    #     """POST: Create or update exactly one model instance.

    #     Return RestResponse(data, status)
    #     """
    #     unique_data, update_data = self.split_data(data)

    #     if data["name_id"] is None:
    #         logger.warning("[API][create_one] Skipping invalid data with missing name_id: {0}".format(str(data)))
    #         return RestResponse(data, status=status.HTTP_400_BAD_REQUEST)

    #     logger.debug(
    #         "[API][create_one] Creating/updating with unique fields {0}, data {1}".format(
    #             str(unique_data), str(update_data)))
    #     try:
    #         obj, created = self.model.objects.get_or_create(**unique_data)
    #         verb = "created" if created else "updated"
    #         self.model.objects.filter(**unique_data).update(**update_data)
    #         obj.save()  # to update caches
    #         # if created:
    #         logger.info("[API][create_one] {0} {1}: {2}".format(
    #             verb, self.model._meta.verbose_name, str(unique_data)))
    #         # else:
    #         # logger.info("[API][create_one] {0} {1} ({2}): {3}".format(
    #         # verb, self.model._meta.verbose_name, obj.pk, obj))
    #         return RestResponse(data, status=status.HTTP_200_OK)
    #     except:
    #         logger.warning("[API][create_one] Failed with {0}".format(str(data)))


router.register("vernaculars", HbvVernacularViewSet)


class HbvXrefViewSet(BatchUpsertViewSet):
    """View set for HbvXref. See HBV Names for details and usage examples."""

    queryset = HbvXref.objects.all()
    serializer_class = HbvXrefSerializer
    filter_class = HbvXrefFilter
    model = HbvXref
    uid_fields = ("xref_id",)

    def fetch_existing_records(self, new_records, model):
        """Fetch pk, (status if QC mixin), and **uid_fields values from a model."""
        return model.objects.filter(
            xref_id__in=list(set([x["xref_id"] for x in new_records]))
        ).values("pk", "xref_id")


router.register("xrefs", HbvXrefViewSet)


class HbvParentViewSet(OgcFidBatchUpsertViewSet):
    """View set for HbvParent. See HBV Names for details and usage examples."""

    queryset = HbvParent.objects.all()
    serializer_class = HbvParentSerializer
    filter_class = HbvParentFilter
    model = HbvParent
    uid_fields = ("ogc_fid", )


router.register("parents", HbvParentViewSet)


# ----------------------------------------------------------------------------#
# Taxon
#
class TaxonSerializer(serializers.ModelSerializer):
    """Serializer for Taxon.

    Includes a summary of conservation status which is ingested into WACensus.

    Example:

    NAME_ID | CONSV_CODE    | LIST_CODE | EPBC  | WA_IUCN   | IUCN_CRITERIA
    228     | 3             | Priority  |       |           |
    297     | T             | WCA_1991  | EN    | VU        | D1+2
    436     | T             | WCA_1991  | EN    | EN        | B1+2c
    """

    # taxon_occurrences = OccurrenceTaxonAreaEncounterPolyInlineSerializer(many=True) # yeah nah

    # is_currently_listed = serializers.ReadOnlyField()
    # conservation_code_state = serializers.ReadOnlyField()           # consv_code
    # conservation_list_state = serializers.ReadOnlyField()           # list_code
    # conservation_category_state = serializers.ReadOnlyField()       # wa_iucn (primary)
    # conservation_categories_state = serializers.ReadOnlyField()     # wa_iucn (all)
    # conservation_criteria_state = serializers.ReadOnlyField()       # iucn_criteria
    # conservation_category_national = serializers.ReadOnlyField()    # epbc

    class Meta:
        """Opts."""

        model = Taxon
        # geo_field = "eoo"
        fields = (
            "pk",
            "name_id",
            "name",
            "rank",
            "parent",
            "author",
            "current",
            "publication_status",
            "vernacular_name",
            "vernacular_names",
            "canonical_name",
            "taxonomic_name",
            "paraphyletic_groups"
            # "is_currently_listed",
            # "conservation_code_state",
            # "conservation_list_state",
            # "conservation_category_state",
            # "conservation_categories_state",
            # "conservation_criteria_state",
            # "conservation_category_national",
        )


class FastTaxonSerializer(serializers.ModelSerializer):
    """Minimal serializer for Taxon to be used in other serializers."""

    class Meta:
        """Opts."""

        model = Taxon
        fields = (
            "pk",
            "name_id",
            "canonical_name",
            "taxonomic_name",
            "vernacular_names",
        )


class TaxonFilter(filters.FilterSet):
    """Taxon filter."""

    current = rf_filters.BooleanFilter(field_name="current")

    class Meta:
        """Class opts."""

        model = Taxon
        fields = {
            "name_id": ["exact", ],
            "name": ["icontains", ],
            "rank": ["icontains", "in", "gt", "gte", "lt", "lte"],
            # "parent": ["exact", ],  # performance bomb
            "publication_status": ["isnull", ],
            # current: provided through field
            "author": ["icontains", ],
            "canonical_name": ["icontains", ],
            "taxonomic_name": ["icontains", ],
            "paraphyletic_groups": ["exact", ],
            # "vernacular_name": ["icontains", ],
            "vernacular_names": ["icontains", ],
            # "eoo" requires polygon filter,

        }


class TaxonViewSet(NameIDBatchUpsertViewSet):
    """View set for Taxon.

    Examples:

    * [Animals](/api/1/taxon/?paraphyletic_groups=20)
    * [Plants sensu latu](/api/1/taxon/?paraphyletic_groups=21)
    * [Only current taxa](/api/1/taxon/?current=true)
    * [Only non-current taxa](/api/1/taxon/?current=false)
    * [Vernacular names contains "woylie" (case insensitive)](/api/1/taxon/?vernacular_names__icontains=woylie) - same works with name, author, can/tax name
    * [NameID exact match](/api/1/taxon/?name_id=25452)
    * [Taxonomic rank Species or lower](/api/1/taxon/?rank__gt=190) - see [Ranks](https://github.com/dbca-wa/wastd/blob/master/taxonomy/models.py#L1613)
    """

    queryset = Taxon.objects.prefetch_related(
        # "paraphyletic_groups",
        # Prefetch("conservation_listings",
        #     queryset=TaxonConservationListing.objects.select_related("taxon")),
        "conservationthreat_set",
        "conservationaction_set",
        "document_set",
    )
    serializer_class = TaxonSerializer
    filter_class = TaxonFilter
    model = Taxon
    uid_fields = ("name_id", )


router.register("taxon", TaxonViewSet, basename="taxon_full")


class FastTaxonViewSet(TaxonViewSet):
    """Fast View set for Taxon."""

    serializer_class = FastTaxonSerializer


router.register("taxon-fast", FastTaxonViewSet, basename="taxon_fast")


# ----------------------------------------------------------------------------#
# Vernacular
#
class VernacularSerializer(serializers.ModelSerializer):
    """Serializer for Vernacular."""

    taxon = FastTaxonSerializer(many=False)

    class Meta:
        """Opts."""

        model = Vernacular
        fields = (
            "ogc_fid",
            "taxon",
            "name",
            "language",
            "preferred",
        )


class VernacularFilter(filters.FilterSet):
    """Vernacular filter."""

    class Meta:
        """Class opts."""

        model = Vernacular
        fields = {
            "ogc_fid": "__all__",
            # "taxon": "__all__",
            "name": "__all__",
            "language": "__all__",
            "preferred": ["exact", ],
        }


class VernacularViewSet(OgcFidBatchUpsertViewSet):
    """View set for Vernacular.

    See HBV Names for details and usage examples.
    All filters are available on all fields.
    """

    queryset = Vernacular.objects.all()
    serializer_class = VernacularSerializer
    filter_class = VernacularFilter
    model = Vernacular
    uid_fields = ("ogc_fid", )


router.register("vernacular", VernacularViewSet)


# ----------------------------------------------------------------------------#
# Crossreference
#
class CrossreferenceSerializer(serializers.ModelSerializer):
    """Serializer for Crossreference."""

    predecessor = FastTaxonSerializer(many=False)
    successor = FastTaxonSerializer(many=False)

    class Meta:
        """Opts."""

        model = Crossreference
        fields = (
            "xref_id",
            "predecessor",
            "successor",
            "reason",
            "authorised_by",
            "authorised_on",
            "effective_to",
            "comments",
        )


class CrossreferenceFilter(filters.FilterSet):
    """Crossreference filter."""

    predecessor = filters.RelatedFilter(TaxonFilter, field_name="predecessor", queryset=Taxon.objects.all())
    successor = filters.RelatedFilter(TaxonFilter, field_name="successor", queryset=Taxon.objects.all())
    # filter_overrides = {
    #     models.DateTimeField: {
    #         'filter_class': filters.IsoDateTimeFilter
    #     },
    # }
    # authorised_on_gte = filters.DateTimeFilter(name="authorised_on", lookup_expr='gte')

    class Meta:
        """Class opts."""

        model = Crossreference
        fields = {
            "xref_id": ["exact", ],
            "reason": ["exact", ],
            "authorised_by": ["exact", ],
            "authorised_on": ["exact", "year__gte", "gt", "gte", "lt", "lte"],
            # "authorised_on_gte": "__all__",
            "effective_to": ["exact", "year__gte", "gt", "gte", "lt", "lte"],
            "comments": ["icontains", ],
        }


class CrossreferenceViewSet(BatchUpsertViewSet):
    """View set for Crossreference.

    See HBV Names for details and usage examples.

    ### Tracing newer names for a Name ID
    See also https://github.com/dbca-wa/wastd/issues/227

    The data shown here are sufficient for the use case, but a convenience method would be faster and, well,  more convenient.

    * [Newer names for Name ID 43353](/api/1/crossreference/?predecessor__name_id=43353) > successor is 43360
    * [Newer names for Name ID 43360](/api/1/crossreference/?predecessor__name_id=43360) > results are [], reached newest name

    ### Tracing older names for a Name ID

    * [Older names for Name ID 43360](/api/1/crossreference/?successor__name_id=43360) > predecessor is 43353
    * [Older names for Name ID 43353](/api/1/crossreference/?successor__name_id=43353) > results are [], reached oldest name

    ### Crossreferences with reason for taxonomic name change:

    * [Reason 0: Misapplied name](/?reason=0)
    * [Reason 1: Taxonomic synonym](/?reason=1)
    * [Reason 2: Nomenclatural synonym](/?reason=2)
    * [Reason 3: Excluded name](/?reason=3)
    * [Reason 4: Concept change](/?reason=4)
    * [Reason 5: Formal description](/?reason=5)
    * [Reason 6: Orthographic variant](/?reason=6)
    * [Reason 7: Name in error](/?reason=7)
    * [Reason 8: Informal Synonym](/?reason=8)

    """

    queryset = Crossreference.objects.all()
    serializer_class = CrossreferenceSerializer
    filter_class = CrossreferenceFilter
    pagination_class = pagination.LimitOffsetPagination
    model = Crossreference
    uid_fields = ("xref_id", )

    def fetch_existing_records(self, new_records, model):
        """Fetch pk, (status if QC mixin), and **uid_fields values from a model."""
        return model.objects.filter(
            xref_id__in=list(set([x["xref_id"] for x in new_records]))
        ).values("pk", "xref_id")


router.register("crossreference", CrossreferenceViewSet)


# ----------------------------------------------------------------------------#
# Community
#
class CommunitySerializer(GeoFeatureModelSerializer):

    class Meta:
        model = Community
        geo_field = "eoo"
        fields = ["code", "name", "description", "eoo"]


class CommunityFilter(filters.FilterSet):
    """Community filter."""

    class Meta:
        """Class opts."""

        model = Community
        fields = {
            "code": "__all__",
            "name": "__all__",
            "description": "__all__",
        }


class CommunityViewSet(BatchUpsertViewSet):
    """View set for Community.

    See HBV Names for details and usage examples.
    All filters are available on all fields.
    """

    queryset = Community.objects.all().prefetch_related(
        "conservation_listings",
        # "conservationthreat_set",
        # "conservationaction_set",
        # "document_set",
    )
    serializer_class = CommunitySerializer
    filter_class = CommunityFilter
    model = Community
    uid_fields = ("code",)

    def fetch_existing_records(self, new_records, model):
        """Fetch pk, (status if QC mixin), and **uid_fields values from a model."""
        return model.objects.filter(
            code__in=list(set([x["code"] for x in new_records]))
        ).values("pk", "code")


router.register("community", CommunityViewSet)
