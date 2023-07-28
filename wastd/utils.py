from collections import namedtuple, OrderedDict
from datetime import date, datetime
from django.contrib.admin.widgets import AdminFileWidget
from django.contrib.gis.db import models
from django.db.models import Q
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotAllowed, Http404, HttpResponse
from django.urls import reverse
from django.utils.encoding import force_str
from django.utils.safestring import mark_safe
from django.utils.text import smart_split
from django.views.generic import ListView, DetailView
from django.views.generic.base import ContextMixin, View
from django_fsm import FSMField, transition
from django_fsm_log.admin import StateLogInline
from django_fsm_log.decorators import fsm_log_by, fsm_log_description
from django_filters import CharFilter
from functools import reduce
from import_export.formats import base_formats
from import_export.resources import Resource
from leaflet.forms.widgets import LeafletWidget
import re
from rest_framework import pagination
from rest_framework.response import Response
from urllib import parse
import uuid


Breadcrumb = namedtuple("Breadcrumb", ["name", "url"])


def sanitize_tag_label(label_string):
    """Return string slugified, uppercased and without dashes."""
    return re.sub(
        r"[-\s]+", "-", (re.sub(r"[^\w\s]", "", label_string).strip().upper())
    )


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


class BreadcrumbContextMixin(ContextMixin):
    """Mixin providing get_breadcrumbs as context object ``breadcrumbs``."""

    def get_context_data(self, **kwargs):
        """Custom context."""
        context = super(BreadcrumbContextMixin, self).get_context_data(**kwargs)
        context["breadcrumbs"] = self.get_breadcrumbs(self.request)
        return context


class ListViewBreadcrumbMixin(BreadcrumbContextMixin, View):
    """ListView mixin providing Breadcrumbs.

    * Home (home)
    * Verbose name plural (list_url)
    """

    def get_breadcrumbs(self, request, obj=None, add=False):
        """Create a list of breadcrumbs as named tuples of ('name', 'url')."""
        return (
            Breadcrumb("Home", reverse("home")),
            Breadcrumb(self.model._meta.verbose_name_plural.capitalize(), None),
        )


class DetailViewBreadcrumbMixin(BreadcrumbContextMixin, View):
    """DetailView mixin providing Breadcrumbs.

    * Home (home)
    * Verbose name plural (list_url)
    * Object (get_absolute_url)
    """

    def get_breadcrumbs(self, request, obj=None, add=False):
        """Create a list of breadcrumbs as named tuples of ('name', 'url')."""
        return (
            Breadcrumb("Home", reverse("home")),
            Breadcrumb(self.model._meta.verbose_name_plural.capitalize(), self.model.list_url()),
            Breadcrumb(self.object.pk, None),
        )


class ResourceDownloadMixin:
    """Copy of the ResourceDownloadMixin class from django-export-download to add XLSX as a format option.
    Reference: https://github.com/soerenbe/django-export-download/blob/master/export_download/views/__init__.py
    """
    resource_class = None
    resource_formats = ['csv', 'xlsx']
    resource_class_parameter = 'resource_class'
    resource_format_parameter = 'resource_format'
    _resource_format_map = {
        'csv': base_formats.CSV,
        'xlsx': base_formats.XLSX,
        'xls': base_formats.XLS,
        'json': base_formats.JSON,
        'yaml': base_formats.YAML,
        'tsv': base_formats.TSV,
    }
    _download_parameter = 'download'

    def _sanity_check(self):
        cn = self.__class__.__name__
        assert issubclass(self.__class__, ListView), 'You can only use the ExportDownloadMixin in a ListView'
        assert self._get_resource_classes(), 'Object {}.resource_class must be defined.'.format(cn)
        for k in self._get_resource_classes():
            assert issubclass(k, Resource), 'Object {} in {}.resource_class is not a instance of import_export.resources.Resource'.format(k, cn)

        assert type(self.resource_formats) is list, 'Format {} in {}.resource_formats is not a valid resource_format'.format(self.resource_formats, cn)
        assert len(self.resource_formats) > 0, 'Format {} in {}.resource_formats must not be empty'.format(self.resource_formats, cn)
        for f in self.resource_formats:
            assert f in self._resource_format_map, 'Format {} in {}.resource_class is not a valid resource_formats'.format(f, cn)

    def _get_resource_classes(self):
        """Format the resource classes.
        """
        if self.resource_class is None:
            return []
        elif isinstance(self.resource_class, list):
            return self.resource_class
        else:
            return [self.resource_class]

    def get_resource_links(self, request):
        """This method return a dict in the form:
        {
            '<resource_format>': ['<download_link>', '<description>'],
            ...
        }
        It is only used when using the export_download_menu templatetag
        """
        resource_links = {}

        for f in self.resource_formats:
            resource_links[f.lower()] = []
            for counter, resource_class in enumerate(self._get_resource_classes()):
                params = request.GET.copy()
                params_class = {
                    self.resource_class_parameter: counter,
                    self.resource_format_parameter: f,
                }
                params.update(params_class)
                link = "?" + self._to_url_params(params)
                # if there is a description field in the resource class
                # we use it to display it as a description
                description = getattr(resource_class, 'description', resource_class.__name__)
                resource_links[f.lower()].append([link, description])
        return resource_links

    def _to_url_params(self, d):
        """Return a kwarg in GET parameter format
        """
        return self._download_parameter + "&" + "&".join('{}={}'.format(k, v) for k, v in d.items())

    def render_to_response(self, *args, **kwargs):
        if self._download_parameter in self.request.GET:
            return self.render_to_download_response(*args, **kwargs)
        return super().render_to_response(*args, **kwargs)

    def render_to_download_response(self, *args, **kwargs):
        self._sanity_check()
        if self.request.method != 'GET':
            return HttpResponseNotAllowed(['GET'])
        # We use the first resource class and first resource format as a default when there are no parameters.
        resource_class = self.request.GET.get(self.resource_class_parameter, 0)
        resource_format = self.request.GET.get(self.resource_format_parameter, self.resource_formats[0])
        if not resource_format:
            raise Http404('You have to pass {} as GET parameter'.format(self.resource_format_parameter))

        selected_format = self._resource_format_map.get(resource_format, None)
        if not selected_format:
            raise Http404('Export format {} not found'.format(resource_format))

        try:
            resource_class_number = int(resource_class)
        except:
            raise Http404('Parameter {} must be an integer'.format(self.resource_class_parameter))
        if resource_class_number >= len(self._get_resource_classes()):
            raise Http404('Parameter {}.{} does not exist'.format(self.__class__.__name__, self.resource_class_parameter))

        qs = self.model.objects.all()
        # If filter_class is defined try to filter against it.
        # You need django-filter to use this feature.
        if hasattr(self, 'filter_class'):
            if self.filter_class:
                qs = self.filter_class(self.request.GET, queryset=qs).qs
        resource_class = self._get_resource_classes()[resource_class_number]
        export = resource_class().export(qs)
        res = getattr(export, selected_format.__name__.lower())
        response = HttpResponse(res, content_type=selected_format.CONTENT_TYPE)
        # Give the response attachment a sane filename.
        response['Content-Disposition'] = 'attachment; filename={}_{}_{}.{}'.format(
            resource_class._meta.model._meta.model_name,
            date.today().isoformat(),
            datetime.now().strftime('%H%M'),
            selected_format.__name__.lower(),
        )
        return response


class MyGeoJsonPagination(pagination.LimitOffsetPagination):
    """
    Paginate GeoJSON with LimitOffset.

    Attempt to un-break HTML filter controls in browsable API.
    Include GET parameter ``no_page`` to deactivate pagination.
    """
    def paginate_queryset(self, queryset, request, view=None):
        """Turn off pagination based on query param ``no_page``."""
        if "no_page" in request.query_params:
            return None
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        """Return a GeoJSON FeatureCollection with pagination links."""
        if "features" in data:
            results = data["features"]
        elif "results" in data:
            results = data["results"]
        else:
            results = data
        return Response(
            OrderedDict(
                [
                    ("type", "FeatureCollection"),
                    ("count", self.count),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("features", results),
                ]
            )
        )


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


class AdminImageWidget(AdminFileWidget):
    def render(self, name, value, attrs=None, renderer=None):
        output = []

        if value and getattr(value, "url", None):
            image_url = value.url
            file_name = str(value)

            output.append(
                f' <a href="{image_url}" target="_blank">'
                f'  <img src="{image_url}" alt="{file_name}" width="150" height="150" '
                f'style="object-fit: cover;"/> </a>'
            )

        output.append(super(AdminFileWidget, self).render(name, value, attrs, renderer))
        return mark_safe("".join(output))


class CustomStateLogInline(StateLogInline):

    classes = (
        "grp-collapse",
        "wide",
        "extrapretty",
    )


class LegacySourceMixin(models.Model):
    """Mixin class for Legacy source and source_id.

    Using this class allows a model to preserve a link to a legacy source.
    This is useful to make a data import repeatable by identifying which records
    to overwrite.
    """

    SOURCE_MANUAL_ENTRY = 0
    SOURCE_PAPER_DATASHEET = 1
    SOURCE_DIGITAL_CAPTURE_ODK = 2
    SOURCE_PARTIAL_SURVEY = 3
    SOURCE_THREATENED_FAUNA = 10
    SOURCE_THREATENED_FLORA = 11
    SOURCE_THREATENED_COMMUNITIES = 12
    SOURCE_THREATENED_COMMUNITIES_BOUNDARIES = 13
    SOURCE_THREATENED_COMMUNITIES_BUFFERS = 14
    SOURCE_THREATENED_COMMUNITIES_SITES = 15
    SOURCE_WAMTRAM2 = 20
    SOURCE_NINGALOO_TURTLE_PROGRAM = 21
    SOURCE_BROOME_TURTLE_PROGRAM = 22
    SOURCE_PORT_HEDLAND_TURTLE_PROGRAM = 23
    SOURCE_GNARALOO_TURTLE_PROGRAM = 24
    SOURCE_ECO_BEACH_TURTLE_PROGRAM = 25
    SOURCE_CETACEAN_STRANDINGS = 30
    SOURCE_PINNIPED_STRANDINGS = 31

    SOURCES = (
        (SOURCE_MANUAL_ENTRY, "Direct entry"),
        (SOURCE_PAPER_DATASHEET, "Manual entry from paper datasheet"),
        (SOURCE_DIGITAL_CAPTURE_ODK, "Digital data capture (ODK)"),
        (SOURCE_PARTIAL_SURVEY, "Partial survey"),
        (SOURCE_THREATENED_FAUNA, "Threatened Fauna"),
        (SOURCE_THREATENED_FLORA, "Threatened Flora"),
        (SOURCE_THREATENED_COMMUNITIES, "Threatened Communities"),
        (SOURCE_THREATENED_COMMUNITIES_BOUNDARIES, "Threatened Communities Boundaries"),
        (SOURCE_THREATENED_COMMUNITIES_BUFFERS, "Threatened Communities Buffers"),
        (SOURCE_THREATENED_COMMUNITIES_SITES, "Threatened Communities Sites"),
        (SOURCE_WAMTRAM2, "Turtle Tagging Database WAMTRAM2"),
        (SOURCE_NINGALOO_TURTLE_PROGRAM, "Ningaloo Turtle Program"),
        (SOURCE_BROOME_TURTLE_PROGRAM, "Broome Turtle Program"),
        (SOURCE_PORT_HEDLAND_TURTLE_PROGRAM, "Pt Hedland Turtle Program"),
        (SOURCE_GNARALOO_TURTLE_PROGRAM, "Gnaraloo Turtle Program"),
        (SOURCE_ECO_BEACH_TURTLE_PROGRAM, "Eco Beach Turtle Program"),
        (SOURCE_CETACEAN_STRANDINGS, "Cetacean Strandings Database"),
        (SOURCE_PINNIPED_STRANDINGS, "Pinniped Strandings Database"),
    )

    source = models.PositiveIntegerField(
        verbose_name="Data Source",
        default=SOURCE_MANUAL_ENTRY,
        choices=SOURCES,
        help_text="Where was this record captured initially?",
    )

    source_id = models.CharField(
        max_length=1000,
        default=uuid.uuid4,
        verbose_name="Source ID",
        help_text="The ID of the record in the original source, if available, or a randomly generated UUID4.",
    )

    class Meta:
        """Class opts."""

        abstract = True
        unique_together = ("source", "source_id")


class UrlsMixin(models.Model):
    """Mixin class to add absolute admin, list, update and detail urls.

    To use, inherit from UrlsMixin and define a custom get_absolute_url(),
    plus any of list/create/update url not following the standard
    {app}:{model}-{action}(**pk) scheme defined in the methods in this mixin.

    This mixin provides the following URLs:

    * absolute_admin_url()
    * get_absolute_url() - available in templates as object.get_absolute_url
    * list_url (classmethod)
    * create_url (classmethod)
    * update_url
    """

    class Meta:
        """Class opts."""

        abstract = True

    # -------------------------------------------------------------------------
    # URLs
    @property
    def absolute_admin_url(self):
        """Return the absolute admin change URL.

        Default: admin:app_model_change(**pk)
        """
        return reverse(
            "admin:{0}_{1}_change".format(self._meta.app_label, self._meta.model_name),
            args=[self.pk],
        )

    def get_absolute_url(self):
        """Detail url, used by Django to link admin to site.

        Default: app:model-detail(**pk).
        """
        return reverse(
            "{0}:{1}-detail".format(self._meta.app_label, self._meta.model_name),
            kwargs={"pk": self.pk},
        )

    @classmethod
    def list_url(cls):
        """List url property. Default: app:model-list."""
        return reverse("{0}:{1}-list".format(cls._meta.app_label, cls._meta.model_name))

    @classmethod
    def create_url(cls):
        """Create url. Default: app:model-create."""
        return reverse(
            "{0}:{1}-create".format(cls._meta.app_label, cls._meta.model_name)
        )

    @property
    def update_url(self):
        """Update url. Default: app:model-update(**pk)."""
        return reverse(
            "{0}:{1}-update".format(self._meta.app_label, self._meta.model_name),
            kwargs={"pk": self.pk},
        )


class QualityControlMixin(models.Model):
    """Mixin class for QA status levels with django-fsm transitions.

    Upcoming work: permissions https://github.com/dbca-wa/wastd/issues/291
    Related: https://github.com/dbca-wa/wastd/issues/299
    """

    STATUS_NEW = "new"
    STATUS_IMPORTED = "imported"
    STATUS_MANUAL_INPUT = "manual input"
    STATUS_PROOFREAD = "proofread"
    STATUS_CURATED = "curated"
    STATUS_PUBLISHED = "published"
    STATUS_FLAGGED = "flagged"
    STATUS_REJECTED = "rejected"

    STATUS_CHOICES = (
        (STATUS_NEW, "New"),
        (STATUS_IMPORTED, "Imported"),
        (STATUS_MANUAL_INPUT, "Manual input"),
        (STATUS_PROOFREAD, "Proofread"),
        (STATUS_CURATED, "Curated"),
        (STATUS_PUBLISHED, "Published"),
        (STATUS_FLAGGED, "Flagged"),
        (STATUS_REJECTED, "Rejected"),
    )

    STATUS_LABELS = {
        STATUS_NEW: "secondary",
        STATUS_IMPORTED: "secondary",
        STATUS_MANUAL_INPUT: "secondary",
        STATUS_PROOFREAD: "warning",
        STATUS_CURATED: "success",
        STATUS_PUBLISHED: "info",
        STATUS_FLAGGED: "warning",
        STATUS_REJECTED: "danger",
    }

    status = FSMField(default=STATUS_NEW, choices=STATUS_CHOICES, verbose_name="QA Status")

    class Meta:
        abstract = True

    @property
    def status_colour(self):
        """Return a Bootstrap4 CSS colour class for each status."""
        return self.STATUS_LABELS[self.status]

    # FSM transitions --------------------------------------------------------#
    def can_proofread(self):
        """Return true if this document can be proofread."""
        return True

    @fsm_log_by
    @transition(
        field=status,
        source=STATUS_NEW,
        target=STATUS_PROOFREAD,
        conditions=[can_proofread],
        # permission=lambda instance, user: user in instance.all_permitted,
        custom=dict(
            verbose="Submit for QA",
            explanation=(
                "Submit this record as a faithful representation of the "
                "data source for QA to become an accepted record."
            ),
            notify=True,
        ),
    )
    def proofread(self, by=None):
        """Mark encounter as proof-read.

        Proofreading compares the attached data sheet with entered values.
        Proofread data is deemed a faithful representation of original data
        captured on a paper field data collection form, or stored in a legacy
        system.
        """
        return

    def can_require_proofreading(self):
        """Return true if this document can be proofread."""
        return True

    @fsm_log_by
    @transition(
        field=status,
        source=STATUS_PROOFREAD,
        target=STATUS_NEW,
        conditions=[can_require_proofreading],
        # permission=lambda instance, user: user in instance.all_permitted,
        custom=dict(
            verbose="Require proofreading",
            explanation=(
                "This record deviates from the data source and "
                "requires proofreading."
            ),
            notify=True,
        ),
    )
    def require_proofreading(self, by=None):
        """Mark encounter as having typos, requiring more proofreading.

        Proofreading compares the attached data sheet with entered values.
        If a discrepancy to the data sheet is found, proofreading is required.
        """
        return

    def can_curate(self):
        """Return true if this record can be accepted."""
        return True

    @fsm_log_by
    @transition(
        field=status,
        source=[STATUS_NEW, STATUS_PROOFREAD, STATUS_FLAGGED],
        target=STATUS_CURATED,
        conditions=[can_curate],
        # permission=lambda instance, user: user in instance.all_permitted,
        custom=dict(
            verbose="Accept as trustworthy",
            explanation=("This record is deemed trustworthy."),
            notify=True,
        ),
    )
    def curate(self, by=None):
        """Accept record as trustworthy.

        Curated data is deemed trustworthy by a subject matter expert.
        Records can be marked as curated from new, proofread, or flagged.
        """
        return

    def can_flag(self):
        """Return true if curated status can be revoked."""
        return True

    @fsm_log_by
    @transition(
        field=status,
        source=STATUS_CURATED,
        target=STATUS_FLAGGED,
        conditions=[can_flag],
        # permission=lambda instance, user: user in instance.all_permitted,
        custom=dict(
            verbose="Flag as not trustworthy",
            explanation=(
                "This record cannot be true. This record requires"
                " review by a subject matter expert."
            ),
            notify=True,
        ),
    )
    def flag(self, by=None):
        """Flag as requiring changes to data.

        Curated data is deemed trustworthy by a subject matter expert.
        Revoking curation flags data for requiring changes by an expert.
        """
        return

    def can_reject(self):
        """Return true if the record can be rejected as entirely wrong."""
        return True

    @fsm_log_by
    @transition(
        field=status,
        source=[STATUS_PROOFREAD, STATUS_CURATED, STATUS_FLAGGED],
        target=STATUS_REJECTED,
        conditions=[can_flag],
        # permission=lambda instance, user: user in instance.all_permitted,
        custom=dict(
            verbose="Confirm as not trustworthy",
            explanation=("This record is confirmed wrong and not trustworthy."),
            notify=True,
        ),
    )
    def reject(self, by=None):
        """Confirm that a record is not trustworthy and beyond repair."""
        return

    def can_reset(self):
        """Return true if the record QA status can be reset."""
        return True

    @fsm_log_by
    @transition(
        field=status,
        source=STATUS_REJECTED,
        target=STATUS_NEW,
        conditions=[can_reset],
        # permission=lambda instance, user: user in instance.all_permitted,
        custom=dict(
            verbose="Reset QA status",
            explanation=("The QA status of this record needs to be reset."),
            notify=True,
        ),
    )
    def reset(self, by=None):
        """Reset the QA status of a record to NEW.

        This allows a record to be brought into the desired QA status.
        """
        return

    def can_publish(self):
        """Return true if this document can be published."""
        return True

    @fsm_log_by
    @transition(
        field=status,
        source=STATUS_CURATED,
        target=STATUS_PUBLISHED,
        conditions=[can_publish],
        # permission=lambda instance, user: user in instance.all_permitted,
        custom=dict(
            verbose="Publish",
            explanation=("This record is fit for release."),
            notify=True,
        ),
    )
    def publish(self, by=None):
        """Mark encounter as ready to be published.

        Published data has been deemed fit for release by the data owner.
        """
        return

    def can_embargo(self):
        """Return true if encounter can be embargoed."""
        return True

    @fsm_log_by
    @transition(
        field=status,
        source=STATUS_PUBLISHED,
        target=STATUS_CURATED,
        conditions=[can_embargo],
        # permission=lambda instance, user: user in instance.all_permitted,
        custom=dict(
            verbose="Embargo",
            explanation=("This record is not fit for release."),
            notify=True,
        ),
    )
    def embargo(self, by=None):
        """Mark encounter as NOT ready to be published.

        Published data has been deemed fit for release by the data owner.
        Embargoed data is marked as curated, but not ready for release.
        """
        return


class CurationMixin(models.Model):
    """Mixin class for curation status levels with django-fsm transitions.
    NOTE: this is a close-duplicate of QualityControlMixin, future task is to consolidate these.
    """
    CURATION_STATUS_NEW = "new"
    CURATION_STATUS_IMPORTED = "imported"
    CURATION_STATUS_MANUAL_INPUT = "manual input"
    CURATION_STATUS_CURATED = "curated"
    CURATION_STATUS_FLAGGED = "flagged"
    CURATION_STATUS_REJECTED = "rejected"
    CURATION_STATUS_CHOICES = (
        (CURATION_STATUS_NEW, "New"),
        (CURATION_STATUS_IMPORTED, "Imported"),
        (CURATION_STATUS_MANUAL_INPUT, "Manual input"),
        (CURATION_STATUS_CURATED, "Curated"),
        (CURATION_STATUS_FLAGGED, "Flagged"),
        (CURATION_STATUS_REJECTED, "Rejected"),
    )
    # Bootstrap CSS colour class for each curation status.
    CURATION_STATUS_LABELS = {
        CURATION_STATUS_NEW: "secondary",
        CURATION_STATUS_IMPORTED: "secondary",
        CURATION_STATUS_MANUAL_INPUT: "secondary",
        CURATION_STATUS_CURATED: "success",
        CURATION_STATUS_FLAGGED: "warning",
        CURATION_STATUS_REJECTED: "danger",
    }

    curation_status = FSMField(default=CURATION_STATUS_NEW, choices=CURATION_STATUS_CHOICES)

    class Meta:
        abstract = True

    @property
    def status_colour(self):
        return self.CURATION_STATUS_LABELS[self.curation_status]

    def can_curate(self):
        """Return true if this record can be accepted."""
        return True

    # New|Imported|Manual input|Flagged -> Curated
    @fsm_log_by
    @fsm_log_description
    @transition(
        field=curation_status,
        source=[CURATION_STATUS_NEW, CURATION_STATUS_IMPORTED, CURATION_STATUS_MANUAL_INPUT, CURATION_STATUS_FLAGGED],
        target=CURATION_STATUS_CURATED,
        conditions=[can_curate],
        custom=dict(
            verbose="Curate as trustworthy",
            explanation=("This record is deemed trustworthy."),
            notify=True,
            url_path="curate/",
            badge="badge-success",
        ),
    )
    def curate(self, by=None, description=None):
        """Accept record as trustworthy.
        Curated data is deemed trustworthy by a subject matter expert.
        """
        return

    def can_flag(self):
        """Return true if curated status can be revoked."""
        return True

    # New|Imported|Manual input|Curated -> Flagged
    @fsm_log_by
    @fsm_log_description
    @transition(
        field=curation_status,
        source=[CURATION_STATUS_NEW, CURATION_STATUS_IMPORTED, CURATION_STATUS_MANUAL_INPUT, CURATION_STATUS_CURATED],
        target=CURATION_STATUS_FLAGGED,
        conditions=[can_flag],
        custom=dict(
            verbose="Flag as not trustworthy",
            explanation=(
                "This record cannot be true. This record requires review by a subject matter expert."
            ),
            notify=True,
            url_path="flag/",
            badge="badge-warning",
        ),
    )
    def flag(self, by=None, description=None):
        """Flag as requiring review by a subject matter expert.
        """
        return

    def can_reject(self):
        """Return true if the record can be rejected as entirely wrong.
        """
        return True

    # New|Imported|Manual input|Flagged -> Rejected
    @fsm_log_by
    @fsm_log_description
    @transition(
        field=curation_status,
        source=[CURATION_STATUS_NEW, CURATION_STATUS_IMPORTED, CURATION_STATUS_MANUAL_INPUT, CURATION_STATUS_FLAGGED],
        target=CURATION_STATUS_REJECTED,
        conditions=[can_reject],
        custom=dict(
            verbose="Reject as not trustworthy",
            explanation=("This record is confirmed wrong and not usable."),
            notify=True,
            url_path="reject/",
            badge="badge-danger",
        ),
    )
    def reject(self, by=None, description=None):
        """Confirm that a record is confirmed wrong and not usable.
        """
        return


S2ATTRS = {"data-width": "50em"}
LEAFLET_WIDGET_ATTRS = {
    "map_height": "700px",
    "map_width": "100%",
    "display_raw": "true",
    "map_srid": 4326,
}
LEAFLET_SETTINGS = {"widget": LeafletWidget(attrs=LEAFLET_WIDGET_ATTRS)}
FORMFIELD_OVERRIDES = {
    models.PointField: LEAFLET_SETTINGS,
    models.MultiPointField: LEAFLET_SETTINGS,
    models.LineStringField: LEAFLET_SETTINGS,
    models.MultiLineStringField: LEAFLET_SETTINGS,
    models.PolygonField: LEAFLET_SETTINGS,
    models.MultiPolygonField: LEAFLET_SETTINGS,
    models.ImageField: {"widget": AdminImageWidget},
    models.FileField: {"widget": AdminImageWidget},
}
FILTER_OVERRIDES = {
    models.CharField: {
        "filter_class": CharFilter,
        "extra": lambda f: {
            "lookup_expr": "icontains",
        },
    },
    models.TextField: {
        "filter_class": CharFilter,
        "extra": lambda f: {
            "lookup_expr": "icontains",
        },
    },
    models.PointField: {
        "filter_class": CharFilter,
        "extra": lambda f: {
            "lookup_expr": "intersects",
            "widget": LeafletWidget(attrs=LEAFLET_SETTINGS),
        },
    },
    models.LineStringField: {
        "filter_class": CharFilter,
        "extra": lambda f: {
            "lookup_expr": "intersects",
            "widget": LeafletWidget(attrs=LEAFLET_SETTINGS),
        },
    },
    models.MultiLineStringField: {
        "filter_class": CharFilter,
        "extra": lambda f: {
            "lookup_expr": "intersects",
            "widget": LeafletWidget(attrs=LEAFLET_SETTINGS),
        },
    },
    models.PolygonField: {
        "filter_class": CharFilter,
        "extra": lambda f: {
            "lookup_expr": "intersects",
            "widget": LeafletWidget(attrs=LEAFLET_SETTINGS),
        },
    },
    models.MultiPolygonField: {
        "filter_class": CharFilter,
        "extra": lambda f: {
            "lookup_expr": "intersects",
            "widget": LeafletWidget(attrs=LEAFLET_SETTINGS),
        },
    },
}
