from wastd.utils import ListResourceView, DetailResourceView
from .models import TurtleTag, TurtlePitTag
from .serializers import TurtleTagSerializer, TurtlePitTagSerializer


class TurtleTagListResource(ListResourceView):
    model = TurtleTag
    serializer = TurtleTagSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        # General-purpose filtering uses the `q` request parameter.
        if 'q' in self.request.GET and self.request.GET['q']:
            queryset = queryset.filter(serial__icontains=self.request.GET['q']).distinct()
        # Where `existing_turtle_id` param is passed in, limit the queryset to tags
        # assigned to that turtle OR unassigned tags.
        # The use-case is the tag select on the turtle observation form, to prevent users
        # from choosing tags assigned to a different turtle.
        if 'existing_turtle_id' in self.request.GET and self.request.GET['existing_turtle_id']:
            pk = int(self.request.GET['existing_turtle_id'])
            queryset = queryset.filter(turtle__pk=pk) | queryset.filter(turtle__isnull=True)
            queryset = queryset.distinct()
        if 'limit' in self.request.GET and self.request.GET['limit']:
            limit = int(self.request.GET['limit'])
            queryset = queryset[0:limit]
        return queryset


class TurtleTagDetailResource(DetailResourceView):
    model = TurtleTag
    serializer = TurtleTagSerializer


class TurtlePitTagListResource(ListResourceView):
    model = TurtlePitTag
    serializer = TurtlePitTagSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        # General-purpose filtering uses the `q` request parameter.
        if 'q' in self.request.GET and self.request.GET['q']:
            queryset = queryset.filter(serial__icontains=self.request.GET['q']).distinct()
        # Where `existing_turtle_id` param is passed in, limit the queryset to tags
        # assigned to that turtle OR unassigned tags.
        # The use-case is the tag select on the turtle observation form, to prevent users
        # from choosing tags assigned to a different turtle.
        if 'existing_turtle_id' in self.request.GET and self.request.GET['existing_turtle_id']:
            pk = int(self.request.GET['existing_turtle_id'])
            queryset = queryset.filter(turtle__pk=pk) | queryset.filter(turtle__isnull=True)
            queryset = queryset.distinct()
        if 'limit' in self.request.GET and self.request.GET['limit']:
            limit = int(self.request.GET['limit'])
            queryset = queryset[0:limit]
        return queryset


class TurtlePitTagDetailResource(DetailResourceView):
    model = TurtlePitTag
    serializer = TurtlePitTagSerializer
