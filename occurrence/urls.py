# -*- coding: utf-8 -*-
"""Taxonomy urls."""
from django.urls import path

from . import views
# from . import wms_config

app_name = 'occurrence'

urlpatterns = [

    # # This creates a WMS endpoint
    # path('wms/',
    #     wms_config.OccWmsView.as_view(),
    #     name='occ_wms'),

    # # This creates a TMS endpoint
    # path('tile/(?P<layers>[^/]+)/(?P<z>[0-9]+)/(?P<x>[0-9]+)/(?P<y>[0-9]+)(?P<format>\.jpg|\.png)',
    #     wms_config.MyWmsView.as_view(),
    #     name='occ_tms'),

    # ------------------------------------------------------------------------#
    # Species: TaxonAreaEncounter
    path('species/',
            views.TaxonAreaEncounterListView.as_view(),
            name='taxonareaencounter-list'),

    path('species/<name_id>/report/',
            views.TaxonAreaEncounterCreateView.as_view(),
            name='taxon-occurrence-create'),

    path('species/<name_id>/area/<area_code>/report/',
            views.TaxonAreaEncounterCreateView.as_view(),
            name='taxon-occurrence-area-create'),

    path('report-species/',
            views.TaxonAreaEncounterCreateView.as_view(),
            name='taxonareaencounter-create'),

    path('species/<pk>/',
            views.TaxonAreaEncounterDetailView.as_view(),
            name='taxonareaencounter-detail'),

    path('species/<pk>/update/',
            views.TaxonAreaEncounterUpdateView.as_view(),
            name='taxonareaencounter-update'),

    # ------------------------------------------------------------------------#
    # Communities: CommunityAreaEncounter
    path('communities/',
            views.CommunityAreaEncounterListView.as_view(),
            name='communityareaencounter-list'),

    path('communities/<int:pk>/report/',
            views.CommunityAreaEncounterCreateView.as_view(),
            name='community-occurrence-create'),

    path('communities/<int:pk>/area/<area_code>/report/',
            views.CommunityAreaEncounterCreateView.as_view(),
            name='community-occurrence-area-create'),

    path('report-community/',
            views.CommunityAreaEncounterCreateView.as_view(),
            name='communityareaencounter-create'),

    path('communities/<int:pk>/',
            views.CommunityAreaEncounterDetailView.as_view(),
            name='communityareaencounter-detail'),

    path('communities/<int:pk>/update/',
            views.CommunityAreaEncounterUpdateView.as_view(),
            name='communityareaencounter-update'),

    # ------------------------------------------------------------------------#
    # Occurrence ObsGroups
    path('<int:occ_pk>/file-attachment/report/',
            views.FileAttachmentCreateView.as_view(),
            name='fileattachment-create'),

    path('<int:occ_pk>/file-attachment/<int:obs_pk>/',
            views.FileAttachmentUpdateView.as_view(),
            name='fileattachment-update'),

    path('<int:occ_pk>/habitat-composition/report/',
            views.HabitatCompositionCreateView.as_view(),
            name='habitatcomposition-create'),

    path('<int:occ_pk>/habitat-composition/<int:obs_pk>/',
            views.HabitatCompositionUpdateView.as_view(),
            name='habitatcomposition-update'),

    path('<int:occ_pk>/area-assessment/report/',
            views.AreaAssessmentCreateView.as_view(),
            name='areaassessment-create'),

    path('<int:occ_pk>/area-assessment/<int:obs_pk>/',
            views.AreaAssessmentUpdateView.as_view(),
            name='areaassessment-update'),

    path('<int:occ_pk>/habitat-condition/report/',
            views.HabitatConditionCreateView.as_view(),
            name='habitatcondition-create'),

    path('<int:occ_pk>/habitat-condition/<int:obs_pk>/',
            views.HabitatConditionUpdateView.as_view(),
            name='habitatcondition-update'),

    path('<int:occ_pk>/fire-history/report/',
            views.FireHistoryCreateView.as_view(),
            name='firehistory-create'),

    path('<int:occ_pk>/fire-history/<int:obs_pk>/',
            views.FireHistoryUpdateView.as_view(),
            name='firehistory-update'),

    path('<int:occ_pk>/plant-count/report/',
            views.PlantCountCreateView.as_view(),
            name='plantcount-create'),

    path('<int:occ_pk>/plant-count/<int:obs_pk>/',
            views.PlantCountUpdateView.as_view(),
            name='plantcount-update'),

    path('<int:occ_pk>/vegetation-classification/report/',
            views.VegetationClassificationCreateView.as_view(),
            name='vegetationclassification-create'),

    path('<int:occ_pk>/vegetation-classification/<int:obs_pk>/',
            views.VegetationClassificationUpdateView.as_view(),
            name='vegetationclassification-update'),

    path('(<int:occ_pk>\d+)/associated-species/report/',
            views.AssociatedSpeciesCreateView.as_view(),
            name='associatedspecies-create'),

    path('<int:occ_pk>\d+)/associated-species/<int:obs_pk>/',
            views.AssociatedSpeciesUpdateView.as_view(),
            name='associatedspecies-update'),

    path('(<int:occ_pk>/animal-observation/report/',
            views.AnimalObservationCreateView.as_view(),
            name='animalobservation-create'),

    path('<int:occ_pk>/animal-observation/<int:obs_pk>/',
            views.AnimalObservationUpdateView.as_view(),
            name='animalobservation-update'),

    path('<int:occ_pk>/physical-sample/report/',
            views.PhysicalSampleCreateView.as_view(),
            name='physicalsample-create'),

    path('<int:occ_pk>/physical-sample/<int:obs_pk>/',
            views.PhysicalSampleUpdateView.as_view(),
            name='physicalsample-update'),
]
