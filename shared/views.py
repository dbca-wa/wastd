from datetime import date, datetime
from django.views.generic.base import ContextMixin, View
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseNotAllowed, Http404, HttpResponse
from django.views.generic.list import ListView
from import_export.formats import base_formats
from import_export.resources import Resource

from shared.utils import Breadcrumb


class SuccessUrlMixin(View):
    """View mixin providing get_success_url as get_absolute_url."""

    def get_success_url(self):
        """Success URL is get_absolute_url."""
        return self.object.get_absolute_url()


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
            Breadcrumb(_("Home"), reverse("home")),
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
            Breadcrumb(_("Home"), reverse("home")),
            Breadcrumb(self.model._meta.verbose_name_plural.capitalize(), self.model.list_url()),
            Breadcrumb(self.object.pk, None),
        )


class UpdateViewBreadcrumbMixin(BreadcrumbContextMixin, View):
    """UpdateView mixin providing Breadcrumbs.

    * Home (home)
    * Verbose name plural (list_url)
    * Object (get_absolute_url)
    * Update (no URL)
    """

    def get_breadcrumbs(self, request, obj=None, add=False):
        """Create a list of breadcrumbs as named tuples of ('name', 'url')."""
        return (
            Breadcrumb(_("Home"), reverse("home")),
            Breadcrumb(self.model._meta.verbose_name_plural, self.object.list_url()),
            Breadcrumb(self.object.pk, self.object.get_absolute_url()),
            Breadcrumb("Update", None),
        )


class CreateViewBreadcrumbMixin(BreadcrumbContextMixin, View):
    """CreateView mixin providing Breadcrumbs.

    * Home (home)
    * Verbose name plural (list_url)
    * Create (no URL)
    """

    def get_breadcrumbs(self, request, obj=None, add=False):
        """Create a list of breadcrumbs as named tuples of ('name', 'url')."""
        return (
            Breadcrumb(_("Home"), reverse("home")),
            # Breadcrumb(self.model._meta.verbose_name_plural, self.model.list_url()),
            Breadcrumb("Create a new {0}".format(self.model._meta.verbose_name), None),
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
