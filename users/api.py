from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotFound

from wastd.utils import DetailResourceView, ListResourceView, search_filter

from .models import User
from .serializers import UserSerializer


class UserListResource(LoginRequiredMixin, ListResourceView):
    model = User
    serializer = UserSerializer

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponseNotFound()
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        # General-purpose filtering uses the `q` request parameter.
        if "q" in self.request.GET and self.request.GET["q"]:
            from .admin import UserAdmin

            q = search_filter(UserAdmin.search_fields, self.request.GET["q"])
            queryset = queryset.filter(q).distinct()
        return queryset


class UserDetailResource(LoginRequiredMixin, DetailResourceView):
    model = User
    serializer = UserSerializer

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponseNotFound()
        return super().dispatch(request, *args, **kwargs)
