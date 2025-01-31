from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.incident_form, name='create_incident'),
    path('list/', views.incident_list, name='incident_list'),
    path('<int:pk>/update/', views.incident_form, name='update_incident'),
    path('export/', views.export_form, name='export_form'),
    path('export/data/', views.export_data, name='export_data'),
    path('get-locations/', views.get_locations, name='get_locations'),
    path('import/', views.import_incidents, name='import_incidents'),
]