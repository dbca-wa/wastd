# -*- coding: utf-8 -*-
"""Conservation urls."""
from django.urls import path

from . import views

app_name = 'conservation'

urlpatterns = [
    path('threats/',
            views.ConservationThreatListView.as_view(),
            name="conservationthreat-list"),
    path('threats/<int:pk>/',
            views.ConservationThreatDetailView.as_view(),
            name="conservationthreat-detail"),
    path('threats/<int:pk>/update/',
            views.ConservationThreatUpdateView.as_view(),
            name="conservationthreat-update"),
    path('threats/create/',
            views.ConservationThreatCreateView.as_view(),
            name="conservationthreat-create"),

    path('actions/',
            views.ConservationActionListView.as_view(),
            name="conservationaction-list"),
    path('actions/<int:pk>/',
            views.ConservationActionDetailView.as_view(),
            name="conservationaction-detail"),
    path('actions/<int:pk>/update/',
            views.ConservationActionUpdateView.as_view(),
            name="conservationaction-update"),
    path('actions/create/',
            views.ConservationActionCreateView.as_view(),
            name="conservationaction-create"),

    path('actions/<int:pk>/report-progress/',
            views.ConservationActivityCreateView.as_view(),
            name="conservationactivity-create"),
    path('actions/activities/<int:pk>/update/',
            views.ConservationActivityUpdateView.as_view(),
            name="conservationactivity-update"),

    path('nominate-taxon/',
            views.TaxonConservationListingCreateView.as_view(),
            name="taxonconservationlisting-create"),
    path('nominate-community/',
            views.CommunityConservationListingCreateView.as_view(),
            name="communityconservationlisting-create"),

    path('documents/',
            views.DocumentListView.as_view(),
            name="document-list"),
    path('documents/create/',
            views.DocumentCreateView.as_view(),
            name="document-create"),
    path('documents/<int:pk>/',
            views.DocumentDetailView.as_view(),
            name="document-detail"),
    path('documents/<int:pk>/update/',
            views.DocumentUpdateView.as_view(),
            name="document-update"),
]
