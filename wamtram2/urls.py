from django.urls import path
from . import views

app_name = "wamtram2"


urlpatterns = [
    path("", views.TurtleListView.as_view(), name="home"),
    path("turtles/", views.TurtleListView.as_view(), name="turtle_list"),
    path("turtles/<int:pk>/", views.TurtleDetailView.as_view(), name="turtle_detail"),
    path('TrtDataEntry/', views.TrtDataEntryView, name='TrtDataEntry'),
    #path('my-autocomplete/', views.MyAutocompleteView.as_view(), name='my-autocomplete'),
]
