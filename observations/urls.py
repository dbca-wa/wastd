from django.urls import path
from . import views

app_name = "observations"

urlpatterns = [
    path("encounters/", views.EncounterList.as_view(), name="encounter-list"),
    path("encounters/<int:pk>/", views.EncounterDetail.as_view(), name="encounter-detail"),
    path("encounters/<int:pk>/update-survey/", views.EncounterUpdateSurvey.as_view(), name="encounter-update-survey"),
    path("animal-encounters/", views.AnimalEncounterList.as_view(), name="animalencounter-list"),
    path("animal-encounters/<int:pk>/", views.AnimalEncounterDetail.as_view(), name="animalencounter-detail"),
    path("animal-encounters/<int:pk>/curate/", views.AnimalEncounterCurate.as_view(), name="animalencounter-curate"),
    path("animal-encounters/<int:pk>/flag/", views.AnimalEncounterFlag.as_view(), name="animalencounter-flag"),
    path("animal-encounters/<int:pk>/reject/", views.AnimalEncounterReject.as_view(), name="animalencounter-reject"),
    path("surveys/", views.SurveyList.as_view(), name="survey-list"),
    path("surveys/<int:pk>/", views.SurveyDetail.as_view(), name="survey-detail"),
    path("surveys/<int:pk>/merge/", views.SurveyMerge.as_view(), name="survey-merge"),
    path("surveys/<int:pk>/close-duplicates/", views.SurveyCloseDuplicates.as_view(), name="survey-close-duplicates"),
    path("surveys/<int:pk>/make-production", views.SurveyMakeProduction.as_view(), name="survey-make-production"),
    path("turtle-nest-encounters/", views.TurtleNestEncounterList.as_view(), name="turtlenestencounter-list"),
    path("turtle-nest-encounters/<int:pk>/", views.TurtleNestEncounterDetail.as_view(), name="turtlenestencounter-detail"),
    path("turtle-nest-encounters/<int:pk>/curate/", views.TurtleNestEncounterCurate.as_view(), name="turtlenestencounter-curate"),
    path("turtle-nest-encounters/<int:pk>/flag/", views.TurtleNestEncounterFlag.as_view(), name="turtlenestencounter-flag"),
    path("turtle-nest-encounters/<int:pk>/reject/", views.TurtleNestEncounterReject.as_view(), name="turtlenestencounter-reject"),
    path("line-transect-encounters/", views.LineTransectEncounterList.as_view(), name="linetransectencounter-list"),
    path("line-transect-encounters/<int:pk>/", views.LineTransectEncounterDetail.as_view(), name="linetransectencounter-detail"),
    path("turtle-nest-disturbance-observations/", views.TurtleNestDisturbanceObservationList.as_view(), name="turtlenestdisturbanceobservation-list"),
    path("disturbance-observations/", views.DisturbanceObservationList.as_view(), name="disturbanceobservation-list"),
    path("track-tally-observations/", views.TrackTallyObservationList.as_view(), name="tracktallyobservation-list"),
    # Satellite view for Area
    path("area/<int:pk>/satellite/", views.AreaSatelliteView.as_view(), name="area-satellite"),
]
