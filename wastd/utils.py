from django.conf import settings
from django.db.models import Q
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils.encoding import force_str
from django.utils.text import smart_split
from django.views.generic import ListView, DetailView
from functools import reduce
import requests
from urllib import parse


def split_text_query(query):
    """Filter stopwords, but only if there are also other words.
    """
    stopwords = '''a,am,an,and,as,at,be,by,can,did,do,for,get,got,
        had,has,he,her,him,his,how,i,if,in,is,it,its,let,may,me,
        my,no,nor,not,of,off,on,or,our,own,say,says,she,so,than,
        that,the,them,then,they,this,to,too,us,was,we,were,what,
        when,who,whom,why,will,yet,you,your'''.split(',')
    split_query = list(smart_split(query))
    filtered_query = [word for word in split_query if word not in stopwords]

    return filtered_query if len(filtered_query) else split_query


def search_filter(search_fields, query_string):
    """search_fields example: ['name', 'category__name', 'description', 'id']
    Returns a Q filter, use like so: MyModel.objects.filter(Q)
    """
    query_string = query_string.strip()
    filters = []
    null_filter = Q(pk=None)

    for word in split_text_query(query_string):
        queries = [Q(**{'{}__icontains'.format(field_name): word}) for field_name in search_fields]
        filters.append(reduce(Q.__or__, queries))

    return reduce(Q.__and__, filters) if len(filters) else null_filter


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
    """Generic API list view, having filtering and pagination options as request params.
    Extend with a `model` and `serializer` class.
    """
    http_method_names = ['get', 'options', 'trace']
    model = None
    serializer = None

    def dispatch(self, request, *args, **kwargs):
        # Sanity-check request params.
        if 'offset' in self.request.GET and self.request.GET['offset']:
            try:
                int(self.request.GET['offset'])
            except:
                return HttpResponseBadRequest()
        if 'limit' in self.request.GET and self.request.GET['limit']:
            try:
                int(self.request.GET['limit'])
            except:
                return HttpResponseBadRequest()
        # FIXME: handle user access authorisation in this method.
        return super().dispatch(request, *args, **kwargs)

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
    """Generic API detail (single object) view.
    Extend with a `model` and `serializer` class.
    """
    http_method_names = ['get', 'options', 'trace']
    model = None
    serializer = None

    def dispatch(self, request, *args, **kwargs):
        # Handle user access authorisation in this method.
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        data = self.serializer.serialize(obj)
        return JsonResponse(data, safe=False)


def get_odk_auth_headers(url=None, email=None, password=None):
    """Returns a dict containing authorization headers for ODK.
    """
    if not url:
        url = settings.ODK_API_URL
    if not email:
        email = settings.ODK_API_EMAIL
    if not password:
        password = settings.ODK_API_PASSWORD

    headers = {"Content-Type": "application/json"}
    data = {
        "email": email,
        "password": password,
    }
    resp = requests.post(f"{url}/sessions", headers=headers, json=data)
    resp.raise_for_status()
    token = resp.json()["token"]
    headers["Authorization"] = f"Bearer {token}"

    return headers


def get_odk_form_submissions(project_id, form_id, form_version, url=None, auth_headers=None):
    """Returns all submissions to an ODK form, as JSON.
    """
    if not url:
        url = settings.ODK_API_URL
    if not auth_headers:
        auth_headers = get_odk_auth_headers()

    resp = requests.get(f"{url}/projects/{project_id}/forms/{form_id}/submissions", headers=auth_headers)
    resp.raise_for_status()

    return resp.json()
