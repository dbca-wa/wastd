from django.urls import path
from . import views

app_name = "turtle_tags"


urlpatterns = [
    path("", views.TurtleList.as_view(), name="home"),
    path("turtles/", views.TurtleList.as_view(), name="turtle_list"),
    path("turtles/<int:pk>/", views.TurtleDetail.as_view(), name="turtle_detail"),
]
