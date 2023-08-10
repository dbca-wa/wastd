from django.urls import path
from rest_framework.routers import DefaultRouter
from users import api as users_api
from observations import api as observations_api

from observations.api_v2 import (
    AreaListResource,
    AreaDetailResource,
    SurveyListResource,
    SurveyDetailResource,
    SurveyMediaAttachmentListResource,
    SurveyMediaAttachmentDetailResource,
    EncounterListResource,
    EncounterDetailResource,
    AnimalEncounterListResource,
    AnimalEncounterDetailResource,
    TurtleNestEncounterListResource,
    TurtleNestEncounterDetailResource,
    MediaAttachmentListResource,
    MediaAttachmentDetailResource,
    TurtleNestObservationListResource,
    TurtleNestObservationDetailResource,
    TurtleHatchlingEmergenceObservationListResource,
    TurtleHatchlingEmergenceObservationDetailResource,
    NestTagObservationListResource,
    NestTagObservationDetailResource,
    TurtleNestDisturbanceObservationListResource,
    TurtleNestDisturbanceObservationDetailResource,
    LoggerObservationListResource,
    LoggerObservationDetailResource,
    HatchlingMorphometricObservationListResource,
    HatchlingMorphometricObservationDetailResource,
    TurtleHatchlingEmergenceOutlierObservationListResource,
    TurtleHatchlingEmergenceOutlierObservationDetailResource,
    LightSourceObservationListResource,
    LightSourceObservationDetailResource,
)
from tagging.api import (
    TurtleTagListResource,
    TurtleTagDetailResource,
    TurtlePitTagListResource,
    TurtlePitTagDetailResource,
)
from users.api_v2 import UserListResource, UserDetailResource


# V2 API URL patterns
urlpatterns = [
    path('users/', UserListResource.as_view(), name='user_list_resource'),
    path('users/<int:pk>/', UserDetailResource.as_view(), name='user_detail_resource'),
    path('areas/', AreaListResource.as_view(), name='area_list_resource'),
    path('areas/<int:pk>/', AreaDetailResource.as_view(), name='area_detail_resource'),
    path('surveys/', SurveyListResource.as_view(), name='survey_list_resource'),
    path('surveys/<int:pk>/', SurveyDetailResource.as_view(), name='survey_detail_resource'),
    path('survey-media-attachments/', SurveyMediaAttachmentListResource.as_view(), name='survey_media_attachment_list_resource'),
    path('survey-media-attachments/<int:pk>/', SurveyMediaAttachmentDetailResource.as_view(), name='survey_media_attachment_detail_resource'),
    path('encounters/', EncounterListResource.as_view(), name='encounter_list_resource'),
    path('encounters/<int:pk>/', EncounterDetailResource.as_view(), name='encounter_detail_resource'),
    path('animal-encounters/', AnimalEncounterListResource.as_view(), name='animal_encounter_list_resource'),
    path('animal-encounters/<int:pk>/', AnimalEncounterDetailResource.as_view(), name='animal_encounter_detail_resource'),
    path('turtle-nest-encounters/', TurtleNestEncounterListResource.as_view(), name='turtle_nest_encounter_list_resource'),
    path('turtle-nest-encounters/<int:pk>/', TurtleNestEncounterDetailResource.as_view(), name='turtle_nest_encounter_detail_resource'),
    path('media-attachments/', MediaAttachmentListResource.as_view(), name='media_attachment_list_resource'),
    path('media-attachments/<int:pk>/', MediaAttachmentDetailResource.as_view(), name='media_attachment_detail_resource'),
    path('turtle-nest-observations/', TurtleNestObservationListResource.as_view(), name='turtle_nest_observation_list_resource'),
    path('turtle-nest-observations/<int:pk>/', TurtleNestObservationDetailResource.as_view(), name='turtle_nest_observation_detail_resource'),
    path('turtle-hatchling-emergence-observations/', TurtleHatchlingEmergenceObservationListResource.as_view(), name='turtle_hatchling_emergence_observation_list_resource'),
    path('turtle-hatchling-emergence-observations/<int:pk>/', TurtleHatchlingEmergenceObservationDetailResource.as_view(), name='turtle_hatchling_emergence_observation_detail_resource'),
    path('nest-tag-observations/', NestTagObservationListResource.as_view(), name='nest_tag_observation_list_resource'),
    path('nest-tag-observations/<int:pk>/', NestTagObservationDetailResource.as_view(), name='nest_tag_observation_detail_resource'),
    path('turtle-nest-disturbance-observations/', TurtleNestDisturbanceObservationListResource.as_view(), name='turtle_nest_disturbance_observation_list_resource'),
    path('turtle-nest-disturbance-observations/<int:pk>/', TurtleNestDisturbanceObservationDetailResource.as_view(), name='turtle_nest_disturbance_observation_detail_resource'),
    path('turtle-tags/', TurtleTagListResource.as_view(), name='turtle_tag_list_resource'),
    path('logger-observation/', LoggerObservationListResource.as_view(), name='logger_observation_list_resource'),
    path('logger-observation/<int:pk>/', LoggerObservationDetailResource.as_view(), name='logger_observation_detail_resource'),
    path('hatchling-morphometric-observations/', HatchlingMorphometricObservationListResource.as_view(), name='hatchling_morphometric_observation_list_resource'),
    path('hatchling-morphometric-observations/<int:pk>/', HatchlingMorphometricObservationDetailResource.as_view(), name='hatchling_morphometric_observation_detail_resource'),
    path('turtle-hatchling-emergence-outlier-observations/', TurtleHatchlingEmergenceOutlierObservationListResource.as_view(), name='turtle_hatchling_emergence_outlier_observation_list_resource'),
    path('turtle-hatchling-emergence-outlier-observations/<int:pk>/', TurtleHatchlingEmergenceOutlierObservationDetailResource.as_view(), name='turtle_hatchling_emergence_outlier_observation_detail_resource'),
    path('light-source-observations/', LightSourceObservationListResource.as_view(), name='light_source_list_resource'),
    path('light-source-observations/<int:pk>/', LightSourceObservationDetailResource.as_view(), name='light_source_detail_resource'),
    path('turtle-tags/<int:pk>/', TurtleTagDetailResource.as_view(), name='turtle_tag_detail_resource'),
    path('turtle-pit-tags/', TurtlePitTagListResource.as_view(), name='turtle_pit_tag_list_resource'),
    path('turtle-pit-tags/<int:pk>/', TurtlePitTagDetailResource.as_view(), name='turtle_pit_tag_detail_resource'),
]

# V1 API router
router = DefaultRouter()

router.register("users", users_api.UserViewSet)
router.register("area", observations_api.AreaViewSet)
router.register("campaigns", observations_api.CampaignViewSet)
router.register("surveys", observations_api.SurveyViewSet)
router.register("survey-media-attachments", observations_api.SurveyMediaAttachmentViewSet)

# Encounters
router.register("encounters", observations_api.EncounterViewSet, basename="encounters_full")
router.register("encounters-fast", observations_api.FastEncounterViewSet, basename="encounters_fast")
router.register("encounters-src", observations_api.SourceIdEncounterViewSet, basename="encounters_src")
router.register("animal-encounters", observations_api.AnimalEncounterViewSet)
router.register("turtle-nest-encounters", observations_api.TurtleNestEncounterViewSet)
router.register("line-transect-encounters", observations_api.LineTransectEncounterViewSet)

# General Observations
router.register("observations", observations_api.ObservationViewSet)
router.register("media-attachments", observations_api.MediaAttachmentViewSet)

# Animal Observations
router.register("management-actions", observations_api.ManagementActionViewSet)
router.register("tag-observations", observations_api.TagObservationViewSet)
router.register("turtle-morphometrics", observations_api.TurtleMorphometricObservationViewSet)
router.register("turtle-damage-observations", observations_api.TurtleDamageObservationViewSet)

# Turtle Nest Observations
router.register("turtle-nest-disturbance-observations", observations_api.TurtleNestDisturbanceObservationViewSet)
router.register("nest-tag-observations", observations_api.NestTagObservationViewSet)
router.register("turtle-nest-excavations", observations_api.TurtleNestObservationViewSet)
router.register("turtle-hatchling-morphometrics", observations_api.HatchlingMorphometricObservationViewSet)
router.register("turtle-nest-hatchling-emergences", observations_api.TurtleHatchlingEmergenceObservationViewSet)
router.register("turtle-nest-hatchling-emergence-outliers", observations_api.TurtleHatchlingEmergenceOutlierObservationViewSet)
router.register("turtle-nest-hatchling-emergence-light-sources", observations_api.LightSourceObservationViewSet)
router.register("logger-observations", observations_api.LoggerObservationViewSet)

# Track Tally Obs
router.register("track-tally", observations_api.TrackTallyObservationViewSet)
router.register("turtle-nest-disturbance-tally", observations_api.TurtleNestDisturbanceTallyObservationViewSet)
