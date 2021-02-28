# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url
from django.urls import path


from . import views

urlpatterns = [
    # URL pattern for the UserListView
    url(
        regex=r'^$',
        view=views.UserListView.as_view(),
        name='user-list'
    ),

    # URL pattern for the UserRedirectView
    url(
        regex=r'^~redirect/$',
        view=views.UserRedirectView.as_view(),
        name='redirect'
    ),

    # URL pattern for the UserDetailView

    path('<int:old_pk>/merge_into/<int:new_pk>/', views.merge_users, name='user-merge-auto'),
    path('<int:old_pk>/merge/<int:new_pk>/', views.MergeView.as_view(), name='user-merge-both'),
    path('<int:old_pk>/merge/', views.MergeView.as_view(), name='user-merge-old'),
    path('<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('merge/', views.MergeView.as_view(), name="user-merge"),

]
