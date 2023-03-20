from django.urls import path
from . import views

app_name = "turtle_tag"


urlpatterns = [
    path("turtles/", views.TurtleList.as_view(), name="turtle_list"),
    path("turtles/<int:pk>/", views.TurtleDetail.as_view(), name="turtle_detail"),
]
