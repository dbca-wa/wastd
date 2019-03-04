# -*- coding: utf-8 -*-
"""Taxonomy urls."""
from django.urls import re_path

from . import views

app_name = 'taxonomy'

urlpatterns = [

    # ------------------------------------------------------------------------#
    # Tasks
    re_path(r'^tasks/update-taxon/$',
            views.update_taxon,
            name="task-update-taxon"),

    # ------------------------------------------------------------------------#
    # Species
    re_path(r'^species/$',
            views.TaxonListView.as_view(),
            name='taxon-list'),

    re_path(r'^species/(?P<name_id>[-+]?[0-9]+)/$',
            views.TaxonDetailView.as_view(),
            name='taxon-detail'),

    # ------------------------------------------------------------------------#
    # Communities
    re_path(r'^communities/$',
            views.CommunityListView.as_view(),
            name='community-list'),

    re_path(r'^communities/(?P<pk>\d+)/$',
            views.CommunityDetailView.as_view(),
            name='community-detail'),
]
