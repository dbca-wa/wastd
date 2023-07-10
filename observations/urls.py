from django.urls import path
from . import views

app_name = "observations"

urlpatterns = [
    path("encounters/", views.EncounterList.as_view(), name="encounter-list"),
    path("encounters/<int:pk>/", views.EncounterDetail.as_view(), name="encounter-detail"),
    path("animal-encounters/", views.AnimalEncounterList.as_view(), name="animalencounter-list"),
    path("animal-encounters/create/", views.AnimalEncounterCreate.as_view(), name="animalencounter-create"),
    path("animal-encounters/<int:pk>/", views.AnimalEncounterDetail.as_view(), name="animalencounter-detail"),
    path("animal-encounters/<int:pk>/update/", views.AnimalEncounterUpdate.as_view(), name="animalencounter-update"),
    path("animal-encounters/<int:pk>/curate/", views.AnimalEncounterCurate.as_view(), name="animalencounter-curate"),
    path("animal-encounters/<int:pk>/flag/", views.AnimalEncounterFlag.as_view(), name="animalencounter-flag"),
    path("animal-encounters/<int:pk>/reject/", views.AnimalEncounterReject.as_view(), name="animalencounter-reject"),
    path("surveys/", views.SurveyList.as_view(), name="survey-list"),
    path("surveys/<int:pk>/", views.SurveyDetail.as_view(), name="survey-detail"),
    path("surveys/<int:pk>/close_duplicates", views.close_survey_duplicates, name="survey-close-duplicates"),
    path("turtle-nest-encounters/", views.TurtleNestEncounterList.as_view(), name="turtlenestencounter-list"),
    path("turtle-nest-encounters/<int:pk>/", views.TurtleNestEncounterDetail.as_view(), name="turtlenestencounter-detail"),
    path("turtle-nest-encounters/<int:pk>/curate/", views.TurtleNestEncounterCurate.as_view(), name="turtlenestencounter-curate"),
    path("turtle-nest-encounters/<int:pk>/flag/", views.TurtleNestEncounterFlag.as_view(), name="turtlenestencounter-flag"),
    path("turtle-nest-encounters/<int:pk>/reject/", views.TurtleNestEncounterReject.as_view(), name="turtlenestencounter-reject"),
    path("line-transect-encounters/", views.LineTransectEncounterList.as_view(), name="linetransectencounter-list"),
    path("line-transect-encounters/<int:pk>/", views.LineTransectEncounterDetail.as_view(), name="linetransectencounter-detail"),
]
