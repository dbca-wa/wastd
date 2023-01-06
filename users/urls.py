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
    path('<int:old_pk>/transfer/<int:new_pk>/area/<int:area_pk>', views.transfer_user_view, name='user-transfer-auto'),
    path('<int:old_pk>/transfer/<int:new_pk>/', views.TransferView.as_view(), name='user-transfer-both'),
    path('<int:old_pk>/transfer-at/<int:area_pk>/', views.TransferView.as_view(), name='user-transfer-area'),
    path('<int:old_pk>/transfer/', views.TransferView.as_view(), name='user-transfer-old'),
    path('<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('transfer/', views.TransferView.as_view(), name="user-transfer"),
    path('merge/', views.MergeView.as_view(), name="user-merge"),
]
