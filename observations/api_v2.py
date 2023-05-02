from django.http import JsonResponse
from django.utils.encoding import force_str
from django.views.generic import ListView, DetailView
from urllib import parse

from .models import (
    Encounter,
    Area,
    Survey,
    SurveyMediaAttachment,
)
from .serializers_v2 import (
    EncounterSerializer,
    AreaSerializer,
    SurveySerializer,
    SurveyMediaAttachmentSerializer,
)


def replace_query_param(url, key, val):
    """Given a URL and a key/val pair, set or replace an item in the query
    parameters of the URL, and return the new URL.
    """
    (scheme, netloc, path, query, fragment) = parse.urlsplit(force_str(url))
    query_dict = parse.parse_qs(query, keep_blank_values=True)
    query_dict[force_str(key)] = [force_str(val)]
    query = parse.urlencode(sorted(query_dict.items()), doseq=True)
    return parse.urlunsplit((scheme, netloc, path, query, fragment))


def remove_query_param(url, key):
    """Given a URL and a key/val pair, remove an item in the query
    parameters of the URL, and return the new URL.
    """
    (scheme, netloc, path, query, fragment) = parse.urlsplit(force_str(url))
    query_dict = parse.parse_qs(query, keep_blank_values=True)
    query_dict.pop(key, None)
    query = parse.urlencode(sorted(query_dict.items()), doseq=True)
    return parse.urlunsplit((scheme, netloc, path, query, fragment))


class ListResourceView(ListView):
    http_method_names = ['get', 'options', 'trace']
    serializer = None

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Pagination logic.
        count = queryset.count()
        if 'offset' in request.GET and request.GET['offset']:
            offset = int(request.GET['offset'])
        else:
            offset = 0
        if 'limit' in request.GET and request.GET['limit']:
            limit = int(request.GET['limit'])
        else:
            limit = 100  # Default limit

        # Get "next" URL
        if offset + limit > count:
            next_url = None
        else:
            next_url = request.build_absolute_uri()
            next_url = replace_query_param(next_url, 'offset', offset + limit)

        # Get "previous" URL
        if offset <= 0:
            prev_url = None
        else:
            prev_url = request.build_absolute_uri()
            if offset - limit <= 0:
                prev_url = remove_query_param(prev_url, 'offset')
            else:
                prev_url = replace_query_param(prev_url, 'offset', offset - limit)

        queryset = queryset[offset:offset + limit]

        objects = {
            'type': 'FeatureCollection',
            'count': count,
            'next': next_url,
            'previous': prev_url,
            'features': [],
        }

        for obj in queryset:
            objects['features'].append(self.serializer.serialize(obj))

        return JsonResponse(objects)


class DetailResourceView(DetailView):
    http_method_names = ['get', 'options', 'trace']
    serializer = None

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        data = self.serializer.serialize(obj)
        return JsonResponse(data, safe=False)


class EncounterListResource(ListResourceView):
    model = Encounter
    serializer = EncounterSerializer

    def get_queryset(self):
        return Encounter.objects.all(
        ).prefetch_related(
            'observer',
            'reporter',
            'area',
            'site',
            'survey',
        )


class EncounterDetailResource(DetailResourceView):
    model = Encounter
    serializer = EncounterSerializer


class AreaListResource(ListResourceView):
    model = Area
    serializer = AreaSerializer


class AreaDetailResource(DetailResourceView):
    model = Area
    serializer = AreaSerializer


class SurveyListResource(ListResourceView):
    model = Survey
    serializer = SurveySerializer


class SurveyDetailResource(DetailResourceView):
    model = Survey
    serializer = SurveySerializer


class SurveyMediaAttachmentListResource(ListResourceView):
    model = SurveyMediaAttachment
    serializer = SurveyMediaAttachmentSerializer


class SurveyMediaAttachmentDetailResource(DetailResourceView):
    model = SurveyMediaAttachment
    serializer = SurveyMediaAttachmentSerializer
