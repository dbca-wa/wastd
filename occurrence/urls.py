# -*- coding: utf-8 -*-
"""Taxonomy urls."""
from django.urls import re_path

from . import views
# from . import wms_config

app_name = 'occurrence'

urlpatterns = [

    # # This creates a WMS endpoint
    # re_path(r'^wms/$', 
    #     wms_config.OccWmsView.as_view(), 
    #     name='occ_wms'),

    # # This creates a TMS endpoint
    # re_path(r'^tile/(?P<layers>[^/]+)/(?P<z>[0-9]+)/(?P<x>[0-9]+)/(?P<y>[0-9]+)(?P<format>\.jpg|\.png)$',
    #     wms_config.MyWmsView.as_view(), 
    #     name='occ_tms'),

    # ------------------------------------------------------------------------#
    # Species: TaxonAreaEncounter
    re_path(r'^species/$',
            views.TaxonAreaEncounterListView.as_view(),
            name='taxonareaencounter-list'),

    re_path(r'^species/(?P<name_id>[-+]?[0-9]+)/report/$',
            views.TaxonAreaEncounterCreateView.as_view(),
            name='taxon-occurrence-create'),

    re_path(r'^species/(?P<name_id>[-+]?[0-9]+)/area/(?P<area_code>[\w-]+)/report/$',
            views.TaxonAreaEncounterCreateView.as_view(),
            name='taxon-occurrence-area-create'),

    re_path(r'^report-species/$',
            views.TaxonAreaEncounterCreateView.as_view(),
            name='taxonareaencounter-create'),

    re_path(r'^species/(?P<pk>\d+)/$',
            views.TaxonAreaEncounterDetailView.as_view(),
            name='taxonareaencounter-detail'),

    re_path(r'species/(?P<pk>\d+)/update/$',
            views.TaxonAreaEncounterUpdateView.as_view(),
            name='taxonareaencounter-update'),

    # ------------------------------------------------------------------------#
    # Communities: CommunityAreaEncounter
    re_path(r'^communities/$',
            views.CommunityAreaEncounterListView.as_view(),
            name='communityareaencounter-list'),

    re_path(r'^communities/(?P<pk>\d+)/report/$',
            views.CommunityAreaEncounterCreateView.as_view(),
            name='community-occurrence-create'),

    re_path(r'^communities/(?P<pk>\d+)/area/(?P<area_code>[\w_-]+)/report/$',
            views.CommunityAreaEncounterCreateView.as_view(),
            name='community-occurrence-area-create'),

    re_path(r'^report-community/$',
            views.CommunityAreaEncounterCreateView.as_view(),
            name='communityareaencounter-create'),

    re_path(r'^communities/(?P<pk>\d+)/$',
            views.CommunityAreaEncounterDetailView.as_view(),
            name='communityareaencounter-detail'),

    re_path(r'^communities/(?P<pk>\d+)/update/$',
            views.CommunityAreaEncounterUpdateView.as_view(),
            name='communityareaencounter-update'),

    # ------------------------------------------------------------------------#
    # Occurrence ObsGroups
    re_path(r'^(?P<occ_pk>\d+)/file-attachment/report$',
            views.FileAttachmentCreateView.as_view(),
            name='fileattachment-create'),

    re_path(r'^(?P<occ_pk>\d+)/file-attachment/(?P<obs_pk>\d+)/$',
            views.FileAttachmentUpdateView.as_view(),
            name='fileattachment-update'),

    re_path(r'^(?P<occ_pk>\d+)/habitat-composition/report$',
            views.HabitatCompositionCreateView.as_view(),
            name='habitatcomposition-create'),

    re_path(r'^(?P<occ_pk>\d+)/habitat-composition/(?P<obs_pk>\d+)/$',
            views.HabitatCompositionUpdateView.as_view(),
            name='habitatcomposition-update'),

    re_path(r'^(?P<occ_pk>\d+)/area-assessment/report$',
            views.AreaAssessmentCreateView.as_view(),
            name='areaassessment-create'),

    re_path(r'^(?P<occ_pk>\d+)/area-assessment/(?P<obs_pk>\d+)/$',
            views.AreaAssessmentUpdateView.as_view(),
            name='areaassessment-update'),

    re_path(r'^(?P<occ_pk>\d+)/habitat-condition/report$',
            views.HabitatConditionCreateView.as_view(),
            name='habitatcondition-create'),

    re_path(r'^(?P<occ_pk>\d+)/habitat-condition/(?P<obs_pk>\d+)/$',
            views.HabitatConditionUpdateView.as_view(),
            name='habitatcondition-update'),

    re_path(r'^(?P<occ_pk>\d+)/fire-history/report$',
            views.FireHistoryCreateView.as_view(),
            name='firehistory-create'),

    re_path(r'^(?P<occ_pk>\d+)/fire-history/(?P<obs_pk>\d+)/$',
            views.FireHistoryUpdateView.as_view(),
            name='firehistory-update'),

    re_path(r'^(?P<occ_pk>\d+)/plant-count/report$',
            views.PlantCountCreateView.as_view(),
            name='plantcount-create'),

    re_path(r'^(?P<occ_pk>\d+)/plant-count/(?P<obs_pk>\d+)/$',
            views.PlantCountUpdateView.as_view(),
            name='plantcount-update'),

    re_path(r'^(?P<occ_pk>\d+)/vegetation-classification/report$',
            views.VegetationClassificationCreateView.as_view(),
            name='vegetationclassification-create'),

    re_path(r'^(?P<occ_pk>\d+)/vegetation-classification/(?P<obs_pk>\d+)/$',
            views.VegetationClassificationUpdateView.as_view(),
            name='vegetationclassification-update'),

    re_path(r'^(?P<occ_pk>\d+)/associated-species/report$',
            views.AssociatedSpeciesCreateView.as_view(),
            name='associatedspecies-create'),

    re_path(r'^(?P<occ_pk>\d+)/associated-species/(?P<obs_pk>\d+)/$',
            views.AssociatedSpeciesUpdateView.as_view(),
            name='associatedspecies-update'),

    re_path(r'^(?P<occ_pk>\d+)/animal-observation/report$',
            views.AnimalObservationCreateView.as_view(),
            name='animalobservation-create'),

    re_path(r'^(?P<occ_pk>\d+)/animal-observation/(?P<obs_pk>\d+)/$',
            views.AnimalObservationUpdateView.as_view(),
            name='animalobservation-update'),

    re_path(r'^(?P<occ_pk>\d+)/physical-sample/report$',
            views.PhysicalSampleCreateView.as_view(),
            name='physicalsample-create'),

    re_path(r'^(?P<occ_pk>\d+)/physical-sample/(?P<obs_pk>\d+)/$',
            views.PhysicalSampleUpdateView.as_view(),
            name='physicalsample-update'),

]
