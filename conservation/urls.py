# -*- coding: utf-8 -*-
"""Conservation urls."""
from django.urls import re_path

from . import views

app_name = 'conservation'

urlpatterns = [
    re_path(r'^threats/$',
            views.ConservationThreatListView.as_view(),
            name="conservationthreat-list"),
    re_path(r'^threats/(?P<pk>\d+)/$',
            views.ConservationThreatDetailView.as_view(),
            name="conservationthreat-detail"),
    re_path(r'^threats/(?P<pk>\d+)/update/$',
            views.ConservationThreatUpdateView.as_view(),
            name="conservationthreat-update"),
    re_path(r'^threats/create/$',
            views.ConservationThreatCreateView.as_view(),
            name="conservationthreat-create"),

    re_path(r'^actions/$',
            views.ConservationActionListView.as_view(),
            name="conservationaction-list"),
    re_path(r'^actions/(?P<pk>\d+)/$',
            views.ConservationActionDetailView.as_view(),
            name="conservationaction-detail"),
    re_path(r'^actions/(?P<pk>\d+)/update/$',
            views.ConservationActionUpdateView.as_view(),
            name="conservationaction-update"),
    re_path(r'^actions/create/$',
            views.ConservationActionCreateView.as_view(),
            name="conservationaction-create"),

    re_path(r'^actions/(?P<pk>\d+)/report-progress/$',
            views.ConservationActivityCreateView.as_view(),
            name="conservationactivity-create"),
    re_path(r'^actions/activities/(?P<pk>\d+)/update/$',
            views.ConservationActivityUpdateView.as_view(),
            name="conservationactivity-update"),

    re_path(r'^taxon-conservationlisting/create/$',
            views.TaxonConservationListingCreateView.as_view(),
            name="taxon-conservationlisting-create"),

    re_path(r'^documents/$',
            views.DocumentListView.as_view(),
            name="document-list"),
    re_path(r'^documents/create/$',
            views.DocumentCreateView.as_view(),
            name="document-create"),
    re_path(r'^documents/(?P<pk>\d+)/$',
            views.DocumentDetailView.as_view(),
            name="document-detail"),
    re_path(r'^documents/(?P<pk>\d+)/update/$',
            views.DocumentUpdateView.as_view(),
            name="document-update"),

]
