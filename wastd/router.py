from rest_framework.routers import DefaultRouter
from wastd.users import api as users_api
from wastd.observations import api as observations_api
from conservation import api as conservation_api
from occurrence import api as occurrence_api
from taxonomy import api as taxonomy_api

router = DefaultRouter()
# meta: users, area, surveys
router.register("users", users_api.UserViewSet)
router.register("area", observations_api.AreaViewSet)
router.register("surveys", observations_api.SurveyViewSet)

# Encounters
router.register(
    "encounters",
    observations_api.EncounterViewSet,
    basename="encounters_full")
router.register(
    "encounters-fast",
    observations_api.FastEncounterViewSet,
    basename="encounters_fast")
router.register(
    "encounters-src",
    observations_api.SourceIdEncounterViewSet,
    basename="encounters_src")
router.register(
    "animal-encounters",
    observations_api.AnimalEncounterViewSet)
router.register(
    "turtle-nest-encounters",
    observations_api.TurtleNestEncounterViewSet)
router.register(
    "logger-encounters",
    observations_api.LoggerEncounterViewSet)
router.register(
    "line-transect-encounters",
    observations_api.LineTransectEncounterViewSet)

# General Observations
router.register(
    "observations",
    observations_api.ObservationViewSet)
router.register(
    "media-attachments",
    observations_api.MediaAttachmentViewSet)

# Animal Observations
router.register(
    "management-actions",
    observations_api.ManagementActionViewSet)
router.register(
    "tag-observations",
    observations_api.TagObservationViewSet)
router.register(
    "turtle-morphometrics",
    observations_api.TurtleMorphometricObservationViewSet)
router.register(
    "turtle-damage-observations",
    observations_api.TurtleDamageObservationViewSet)

# Turtle Nest Observations
router.register(
    "turtle-nest-disturbance-observations",
    observations_api.TurtleNestDisturbanceObservationViewSet)
router.register(
    "nest-tag-observations",
    observations_api.NestTagObservationViewSet)
router.register(
    "turtle-nest-excavations",
    observations_api.TurtleNestObservationViewSet)
router.register(
    "turtle-hatchling-morphometrics",
    observations_api.HatchlingMorphometricObservationViewSet)
router.register(
    "turtle-nest-hatchling-emergences",
    observations_api.TurtleHatchlingEmergenceObservationViewSet)
router.register(
    "turtle-nest-hatchling-emergence-outliers",
    observations_api.TurtleHatchlingEmergenceOutlierObservationViewSet)
router.register(
    "turtle-nest-hatchling-emergence-light-sources",
    observations_api.LightSourceObservationViewSet)

# Track Tally Obs
router.register(
    "track-tally",
    observations_api.TrackTallyObservationViewSet)
router.register(
    "turtle-nest-disturbance-tally",
    observations_api.TurtleNestDisturbanceTallyObservationViewSet)
