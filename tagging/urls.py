from django.urls import path
from . import views

app_name = "tagging"


urlpatterns = [
    path("", views.TurtleList.as_view(), name="home"),
    path("turtles/", views.TurtleList.as_view(), name="turtle_list"),
    path("turtles/<int:pk>/", views.TurtleDetail.as_view(), name="turtle_detail"),
    path("observations/", views.TurtleObservationList.as_view(), name="turtleobservation_list"),
    path("observations/<int:pk>/", views.TurtleObservationDetail.as_view(), name="turtleobservation_detail"),
    path("observations/add/", views.TurtleObservationAdd.as_view(), name="turtleobservation_add"),
    # tags
    # pit tags
]
