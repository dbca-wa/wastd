from django.urls import path
from . import views

app_name = "observations"

urlpatterns = [
    path(
        "surveys/<int:pk>/close_duplicates",
        views.close_survey_duplicates,
        name="survey-close-duplicates",
    ),
    path("surveys/<int:pk>/", views.SurveyDetail.as_view(), name="survey-detail"),
    path("surveys/", views.SurveyList.as_view(), name="survey-list"),
    path(
        "encounters/<int:pk>/", views.EncounterDetail.as_view(), name="encounter-detail"
    ),
    path("encounters/", views.EncounterList.as_view(), name="encounter-list"),
    path(
        "animal-encounters/create/",
        views.AnimalEncounterCreate.as_view(),
        name="animalencounter-create",
    ),
    path(
        "animal-encounters/<int:pk>/",
        views.AnimalEncounterDetail.as_view(),
        name="animalencounter-detail",
    ),
    path(
        "animal-encounters/<int:pk>/update/",
        views.AnimalEncounterUpdate.as_view(),
        name="animalencounter-update",
    ),
    path(
        "animal-encounters/",
        views.AnimalEncounterList.as_view(),
        name="animalencounter-list",
    ),
    path(
        "turtle-nest-encounters/<int:pk>/",
        views.TurtleNestEncounterDetail.as_view(),
        name="turtlenestencounter-detail",
    ),
    path(
        "turtle-nest-encounters/",
        views.TurtleNestEncounterList.as_view(),
        name="turtlenestencounter-list",
    ),
    path(
        "line-transect-encounters/<int:pk>/",
        views.LineTransectEncounterDetail.as_view(),
        name="linetransectencounter-detail",
    ),
    path(
        "line-transect-encounters/",
        views.LineTransectEncounterList.as_view(),
        name="linetransectencounter-list",
    ),
    # path('logger-encounters/<int:pk>/', views.LoggerEncounterDetail.as_view(), name='loggerencounter-detail'),
    # path('logger-encounters/', views.LoggerEncounterList.as_view(), name='loggerencounter-list'),
]
