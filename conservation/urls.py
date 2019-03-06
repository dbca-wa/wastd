# -*- coding: utf-8 -*-
"""Conservation urls."""
from django.urls import re_path

from . import views

app_name = 'conservation'

urlpatterns = [
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
]
