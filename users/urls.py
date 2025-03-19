from django.urls import path

from . import views

urlpatterns = [
    path("", views.UserListView.as_view(), name="user-list"),
    path("profile/", views.UserDetailView.as_view(), name="user-profile"),
    path("<int:pk>/", views.UserDetailView.as_view(), name="user-detail"),
    path("<int:old_pk>/merge/<int:new_pk>/", views.UserMergeView.as_view(), name="user-merge-both"),
    path("<int:old_pk>/merge/", views.UserMergeView.as_view(), name="user-merge-old"),
    path("<int:old_pk>/transfer/<int:new_pk>/area/<int:area_pk>", views.transfer_user_view, name="user-transfer-auto"),
    path("<int:old_pk>/transfer/<int:new_pk>/", views.TransferView.as_view(), name="user-transfer-both"),
    path("<int:old_pk>/transfer-at/<int:area_pk>/", views.TransferView.as_view(), name="user-transfer-area"),
    path("<int:old_pk>/transfer/", views.TransferView.as_view(), name="user-transfer-old"),
    path("transfer/", views.TransferView.as_view(), name="user-transfer"),
    path("merge/", views.UserMergeView.as_view(), name="user-merge"),
    path("redirect/", views.UserRedirectView.as_view(), name="redirect"),
]
