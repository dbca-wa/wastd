# -*- coding: utf-8 -*-
"""Taxonomy urls."""
from django.urls import re_path

from . import views

app_name = 'occurrence'

urlpatterns = [
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
    re_path(r'^(?P<occ_pk>\d+)/associated-species/report$',
            views.AssociatedSpeciesObservationCreateView.as_view(),
            name='associatedspeciesobservation-create'),

    re_path(r'^(?P<occ_pk>\d+)/associated-species/(?P<obs_pk>\d+)/$',
            views.AssociatedSpeciesObservationUpdateView.as_view(),
            name='associatedspeciesobservation-update'),

    re_path(r'^(?P<occ_pk>\d+)/fire-history/report$',
            views.FireHistoryObservationCreateView.as_view(),
            name='firehistoryobservation-create'),

    re_path(r'^(?P<occ_pk>\d+)/fire-history/(?P<obs_pk>\d+)/$',
            views.FireHistoryObservationUpdateView.as_view(),
            name='firehistoryobservation-update'),

    re_path(r'^(?P<occ_pk>\d+)/file-attachment/report$',
            views.FileAttachmentObservationCreateView.as_view(),
            name='fileattachmentobservation-create'),

    re_path(r'^(?P<occ_pk>\d+)/file-attachment/(?P<obs_pk>\d+)/$',
            views.FileAttachmentObservationUpdateView.as_view(),
            name='fileattachmentobservation-update'),

    re_path(r'^(?P<occ_pk>\d+)/area-assessment/report$',
            views.AreaAssessmentObservationCreateView.as_view(),
            name='areaassessmentobservation-create'),

    re_path(r'^(?P<occ_pk>\d+)/area-assessment/(?P<obs_pk>\d+)/$',
            views.AreaAssessmentObservationUpdateView.as_view(),
            name='areaassessmentobservation-update'),

]
