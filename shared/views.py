"""View mixins."""
from django.views.generic.base import ContextMixin, View
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

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
        context['breadcrumbs'] = self.get_breadcrumbs(self.request)
        return context


class ListViewBreadcrumbMixin(BreadcrumbContextMixin, View):
    """ListView mixin providing Breadbrumbs.

    * Home (home)
    * Verbose name plural (list_url)
    """

    def get_breadcrumbs(self, request, obj=None, add=False):
        """Create a list of breadcrumbs as named tuples of ('name', 'url')."""
        return (
            Breadcrumb(_('Home'), reverse('home')),
            Breadcrumb(self.model._meta.verbose_name_plural, None)
        )


class DetailViewBreadcrumbMixin(BreadcrumbContextMixin, View):
    """DetailView mixin providing Breadbrumbs.

    * Home (home)
    * Verbose name plural (list_url)
    * Object (get_absolute_url)
    """

    def get_breadcrumbs(self, request, obj=None, add=False):
        """Create a list of breadcrumbs as named tuples of ('name', 'url')."""
        return (
            Breadcrumb(_('Home'), reverse('home')),
            Breadcrumb(self.model._meta.verbose_name_plural, self.model.list_url()),
            Breadcrumb(self.object.__str__(), self.object.get_absolute_url())
        )


class UpdateViewBreadcrumbMixin(BreadcrumbContextMixin, View):
    """UpdateView mixin providing Breadbrumbs.

    * Home (home)
    * Verbose name plural (list_url)
    * Object (get_absolute_url)
    * Update (no URL)
    """

    def get_breadcrumbs(self, request, obj=None, add=False):
        """Create a list of breadcrumbs as named tuples of ('name', 'url')."""
        return (
            Breadcrumb(_('Home'), reverse('home')),
            Breadcrumb(self.model._meta.verbose_name_plural, self.object.list_url()),
            Breadcrumb(self.object.__str__(), self.object.get_absolute_url()),
            Breadcrumb("Update", None)
        )


class CreateViewBreadcrumbMixin(BreadcrumbContextMixin, View):
    """CreateView mixin providing Breadbrumbs.

    * Home (home)
    * Verbose name plural (list_url)
    * Create (no URL)
    """

    def get_breadcrumbs(self, request, obj=None, add=False):
        """Create a list of breadcrumbs as named tuples of ('name', 'url')."""
        return (
            Breadcrumb(_('Home'), reverse('home')),
            # Breadcrumb(self.model._meta.verbose_name_plural, self.model.list_url()),
            Breadcrumb("Create a new {0}".format(self.model._meta.verbose_name), None)
        )
