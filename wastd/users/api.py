from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet

from .models import User


class UserSerializer(ModelSerializer):
    """User serializer."""
    partial = True

    class Meta:
        model = User
        fields = (
            "pk",
            "username",
            "name",
            "nickname",
            "aliases",
            "role",
            "affiliation",
            "email",
            "phone",
            "is_active",
            "alive"
        )


class FastUserSerializer(ModelSerializer):
    """Minimal User serializer."""

    class Meta:
        model = User
        fields = ("pk", "username", "name",)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    uid_field = "pk"
    model = User
    filterset_fields = ['username', 'nickname', 'email', 'aliases', 'phone', 'is_active', 'alive']

    def get_queryset(self):
        queryset = User.objects.all()
        # TODO: undertake fuzzy string matching on user name/username (if required).
        name = self.request.query_params.get('name', None)
        if name is not None:
            queryset = queryset.filter(name=name)
        return queryset
