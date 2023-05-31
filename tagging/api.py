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
        if 'limit' in self.request.GET and self.request.GET['limit']:
            limit = int(self.request.GET['limit'])
            queryset = queryset[0:limit]
        return queryset


class TurtlePitTagDetailResource(DetailResourceView):
    model = TurtlePitTag
    serializer = TurtlePitTagSerializer
