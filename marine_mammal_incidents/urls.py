from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_incident, name='create_incident'),
    path('list/', views.incident_list, name='incident_list'),
    path('<int:pk>/update/', views.update_incident, name='update_incident'),
]