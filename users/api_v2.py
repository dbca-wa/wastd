from wastd.utils import ListResourceView, DetailResourceView
from django.http import HttpResponseNotFound
from .models import User
from .serializers import UserSerializer


class UserListResource(ListResourceView):
    model = User
    serializer = UserSerializer

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponseNotFound("Not found")
        return super().dispatch(request, *args, **kwargs)


class UserDetailResource(DetailResourceView):
    model = User
    serializer = UserSerializer

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponseNotFound("Not found")
        return super().dispatch(request, *args, **kwargs)
