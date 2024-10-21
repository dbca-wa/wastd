from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.incident_form, name='create_incident'),
    path('list/', views.incident_list, name='incident_list'),
    path('<int:pk>/update/', views.incident_form, name='update_incident'),
]