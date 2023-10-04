from wastd.utils import ListResourceView, DetailResourceView
from .models import Turtle, TurtleTag
from .serializers import TurtleSerializer, TurtleTagSerializer


class TurtleListResource(ListResourceView):
    model = Turtle
    serializer = TurtleSerializer


class TurtleDetailResource(DetailResourceView):
    model = TurtleTag
    serializer = TurtleTagSerializer


class TurtleTagListResource(ListResourceView):
    model = TurtleTag
    serializer = TurtleTagSerializer


class TurtleTagDetailResource(DetailResourceView):
    model = TurtleTag
    serializer = TurtleTagSerializer
