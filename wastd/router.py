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


# conservation.ConservationListing -------------------------------------------#
router.register(
    "community-conservationlisting",
    conservation_api.CommunityConservationListingViewSet)
router.register(
    "conservationcategory",
    conservation_api.ConservationCategoryViewSet)
router.register(
    "conservationcriterion",
    conservation_api.ConservationCriterionViewSet)
router.register(
    "conservationlist",
    conservation_api.ConservationListViewSet)
router.register(
    "document",
    conservation_api.DocumentViewSet)
router.register(
    "taxon-conservationlisting",
    conservation_api.TaxonConservationListingViewSet)
# occurrence.AreaEncounter ---------------------------------------------------#
# Without basename, the last registered viewset overrides the other area viewsets
router.register(
    "occ-areas",
    occurrence_api.OccurrenceAreaPolyViewSet,
    basename="occurrence_area_polys")
router.register(
    "occ-area-points",
    occurrence_api.OccurrenceAreaPointViewSet,
    basename="occurrence_area_points")
# Without basename, the last registered viewset overrides the other area viewsets
router.register(
    "occ-taxon-areas",
    occurrence_api.OccurrenceTaxonAreaEncounterPolyViewSet,
    basename="occurrence_taxonarea_polys")
router.register(
    "occ-taxon-points",
    occurrence_api.OccurrenceTaxonAreaEncounterPointViewSet,
    basename="occurrence_taxonarea_points")
# Without basename, the last registered viewset overrides the other area viewsets
router.register(
    "occ-community-areas",
    occurrence_api.OccurrenceCommunityAreaEncounterPolyViewSet,
    basename="occurrence_communityarea_polys")
router.register(
    "occ-community-points",
    occurrence_api.OccurrenceCommunityAreaEncounterPointViewSet,
    basename="occurrence_communityarea_points")
router.register(
    "occ-observation",
    occurrence_api.ObservationGroupViewSet,
    basename="occurrence_observation_group")
# Occurrence Lookups ---------------------------------------------------------#
router.register("lookup-landform", occurrence_api.LandformViewSet)
router.register("lookup-rocktype", occurrence_api.RockTypeViewSet)
router.register("lookup-soiltype", occurrence_api.SoilTypeViewSet)
router.register("lookup-soilcolour", occurrence_api.SoilColourViewSet)
router.register("lookup-drainage", occurrence_api.DrainageViewSet)
router.register("lookup-surveymethod", occurrence_api.SurveyMethodViewSet)
router.register("lookup-soilcondition", occurrence_api.SoilConditionViewSet)
router.register("lookup-countaccuracy", occurrence_api.CountAccuracyViewSet)
router.register("lookup-countmethod", occurrence_api.CountMethodViewSet)
router.register("lookup-countsubject", occurrence_api.CountSubjectViewSet)
router.register("lookup-plantcondition", occurrence_api.PlantConditionViewSet)
router.register("lookup-detectionmethod",
                occurrence_api.DetectionMethodViewSet)
router.register("lookup-confidence", occurrence_api.ConfidenceViewSet)
router.register("lookup-reproductivematurity",
                occurrence_api.ReproductiveMaturityViewSet)
router.register("lookup-animalhealth", occurrence_api.AnimalHealthViewSet)
router.register("lookup-animalsex", occurrence_api.AnimalSexViewSet)
router.register("lookup-causeofdeath", occurrence_api.CauseOfDeathViewSet)
router.register("lookup-secondarysigns", occurrence_api.SecondarySignsViewSet)
router.register("lookup-sampletype", occurrence_api.SampleTypeViewSet)
router.register("lookup-sampledestination",
                occurrence_api.SampleDestinationViewSet)
router.register("lookup-permittype", occurrence_api.PermitTypeViewSet)
# taxonomy
router.register("names", taxonomy_api.HbvNameViewSet)
router.register("supra", taxonomy_api.HbvSupraViewSet)
router.register("groups", taxonomy_api.HbvGroupViewSet)
router.register("families", taxonomy_api.HbvFamilyViewSet)
router.register("genera", taxonomy_api.HbvGenusViewSet)
router.register("species", taxonomy_api.HbvSpeciesViewSet)
router.register("vernaculars", taxonomy_api.HbvVernacularViewSet)
router.register("xrefs", taxonomy_api.HbvXrefViewSet)
router.register("parents", taxonomy_api.HbvParentViewSet)
router.register("taxon", taxonomy_api.TaxonViewSet, basename="taxon_full")
router.register("taxon-fast", taxonomy_api.FastTaxonViewSet,
                basename="taxon_fast")
router.register("vernacular", taxonomy_api.VernacularViewSet)
router.register("crossreference", taxonomy_api.CrossreferenceViewSet)
router.register("community", taxonomy_api.CommunityViewSet)
