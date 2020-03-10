# -*- coding: utf-8 -*-
from django.urls import path
from . import views

app_name = 'taxonomy'

urlpatterns = [
    # ------------------------------------------------------------------------#
    # Tasks
    path('tasks/update-taxon/', views.update_taxon, name="task-update-taxon"),
    # ------------------------------------------------------------------------#
    # Species
    path('species/', views.TaxonListView.as_view(), name='taxon-list'),
    path('species/<name_id>/', views.TaxonDetailView.as_view(), name='taxon-detail'),
    # ------------------------------------------------------------------------#
    # Communities
    path('communities/', views.CommunityListView.as_view(), name='community-list'),
    path('communities/<int:pk>/', views.CommunityDetailView.as_view(), name='community-detail'),
]
