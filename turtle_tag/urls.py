from django.urls import path
from . import views

app_name = "turtle_tag"


urlpatterns = [
    path("", views.TurtleList.as_view(), name="home"),
    path("turtles/", views.TurtleList.as_view(), name="turtle_list"),
    path("turtles/create/", views.TurtleCreate.as_view(), name="turtle_create"),
    path("turtles/<int:pk>/", views.TurtleDetail.as_view(), name="turtle_detail"),
    path("turtles/<int:pk>/tags-update/", views.TurtleTagsUpdate.as_view(), name="turtle_tags_update"),
    path("turtles/<int:pk>/pit-tags-update/", views.TurtlePitTagsUpdate.as_view(), name="turtle_pit_tags_update"),
    path("turtles/<int:pk>/observation-create/", views.TurtleObservationCreate.as_view(), name="turtle_observation_create"),
    path("observations/", views.TurtleObservationList.as_view(), name="turtleobservation_list"),
    path("observations/<int:pk>/", views.TurtleObservationDetail.as_view(), name="turtleobservation_detail"),
    #path("observations/<int:pk>/update/", views.TurtleObservationUpdate.as_view(), name="turtleobservation_update"),
    # tags
    # pit tags
]
