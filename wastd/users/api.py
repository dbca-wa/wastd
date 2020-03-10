from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ModelViewSet

from .models import User


class UserSerializer(ModelSerializer):
    """User serializer."""
    partial = True

    class Meta:
        model = User
        fields = ("pk", "username", "name", "nickname", "aliases", "role", "email", "phone")


class FastUserSerializer(ModelSerializer):
    """Minimal User serializer."""

    class Meta:
        model = User
        fields = ("pk", "username", "name",)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    uid_field = "username"
    model = User
