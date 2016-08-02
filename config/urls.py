# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.admin import site
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView
from django.views import defaults as default_views

from adminactions import actions
from rest_framework import routers, serializers, viewsets
from wastd.observations.models import (Observation, StrandingObservation,
                                       TurtleStrandingObservation,
                                       MediaAttachment, TagObservation)
from wastd.users.models import User
from wastd.observations.views import schema_view
from djgeojson.views import GeoJSONLayerView


# register all adminactions
actions.add_to_site(site)

# API config -----------------------------------------------------------------#
class UserSerializer(serializers.HyperlinkedModelSerializer):
    """User serializer."""

    class Meta:
        """Class options."""

        model = User
        fields = ('name', 'email')


class MediaAttachmentSerializer(serializers.HyperlinkedModelSerializer):
    """MediaAttachment serializer."""

    observation = serializers.HyperlinkedRelatedField(
        source='observation.pk', view_name='observation-detail', read_only=True)

    class Meta:
        """Class options."""

        model = MediaAttachment
        fields = ('observation', 'media_type', 'title', 'attachment')


class TagObservationSerializer(serializers.HyperlinkedModelSerializer):
    """TagObservation serializer."""

    observation = serializers.HyperlinkedRelatedField(
        source='observation.pk', view_name='observation-detail', read_only=True)

    class Meta:
        """Class options."""

        model = TagObservation
        fields = ('observation', 'type', 'status', 'name', 'comments')


class ObservationSerializer(serializers.HyperlinkedModelSerializer):
    """Observation serializer."""

    mediaattachment_set = serializers.HyperlinkedRelatedField(
        many=True, view_name='mediaattachment-detail', read_only=True)
    tagobservation_set = serializers.HyperlinkedRelatedField(
        many=True, view_name='tagobservation-detail', read_only=True)

    class Meta:
        """Class options."""

        model = Observation
        fields = ('where', 'when', 'who',
                  'mediaattachment_set', 'tagobservation_set')
        geo_field = "where"


class StrandingObservationSerializer(serializers.HyperlinkedModelSerializer):
    """StrandingObservation serializer."""

    mediaattachment_set = serializers.HyperlinkedRelatedField(
        many=True, view_name='mediaattachment-detail', read_only=True)
    tagobservation_set = serializers.HyperlinkedRelatedField(
        many=True, view_name='tagobservation-detail', read_only=True)

    class Meta:
        """Class options."""

        model = StrandingObservation
        fields = ('where', 'when', 'who', 'species', 'health', 'behaviour',
                  'mediaattachment_set', 'tagobservation_set',
                  'management_actions', 'comments')
        geo_field = "where"


class TurtleStrandingObservationSerializer(serializers.HyperlinkedModelSerializer):
    """TurtleStrandingObservation serializer."""

    mediaattachment_set = serializers.HyperlinkedRelatedField(
        many=True, view_name='mediaattachment-detail', read_only=True)
    tagobservation_set = serializers.HyperlinkedRelatedField(
        many=True, view_name='tagobservation-detail', read_only=True)

    class Meta:
        """Class options."""

        model = TurtleStrandingObservation
        fields = ('where', 'when', 'who', 'species', 'health', 'behaviour',
                  'mediaattachment_set', 'tagobservation_set',
                  'management_actions', 'comments', 'sex', 'maturity',
                  'curved_carapace_length_mm', 'curved_carapace_length_accuracy',
                  'curved_carapace_width_mm', 'curved_carapace_width_accuracy',
                  'tail_length_mm', 'tail_length_accuracy',
                  'maximum_head_width_mm', 'maximum_head_width_accuracy')
        geo_field = "where"


# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    """User view set."""

    queryset = User.objects.all()
    serializer_class = UserSerializer


class MediaAttachmentViewSet(viewsets.ModelViewSet):
    """MediaAttachment view set."""

    queryset = MediaAttachment.objects.all()
    serializer_class = MediaAttachmentSerializer


class TagObservationViewSet(viewsets.ModelViewSet):
    """TagObservation view set."""

    queryset = TagObservation.objects.all()
    serializer_class = TagObservationSerializer


class ObservationViewSet(viewsets.ModelViewSet):
    """Observation view set."""

    queryset = Observation.objects.all()
    serializer_class = ObservationSerializer


class StrandingObservationViewSet(viewsets.ModelViewSet):
    """StrandingObservation view set."""

    queryset = StrandingObservation.objects.all()
    serializer_class = StrandingObservationSerializer


class TurtleStrandingObservationViewSet(viewsets.ModelViewSet):
    """TurtleStrandingObservation view set."""

    queryset = TurtleStrandingObservation.objects.all()
    serializer_class = TurtleStrandingObservationSerializer


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'media-attachments', MediaAttachmentViewSet)
router.register(r'tag-observation', TagObservationViewSet)
router.register(r'observations', ObservationViewSet)
router.register(r'stranding-observations', StrandingObservationViewSet)
router.register(r'turtle-stranding-observations', TurtleStrandingObservationViewSet)

# End API config -------------------------------------------------------------#

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='pages/home.html'),
        name='home'),

    url(r'^about/$', TemplateView.as_view(template_name='pages/about.html'),
        name='about'),

    url(r'api-docs/1/', schema_view, name="api-docs"),

    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, include(admin.site.urls)),

    # User management
    url(r'^users/', include('wastd.users.urls', namespace='users')),
    url(r'^accounts/', include('allauth.urls')),

    # Your stuff: custom urls includes go here
    # API
    url(r'^api/1/', include(router.urls), name='api'),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^adminactions/', include('adminactions.urls')),
    url(r'^observations.geojson$',
        GeoJSONLayerView.as_view(model=Observation,
                                 properties=('popupContent', ),
                                 geometry_field="where"),
        name='observation-geojson'),

    # Select2 URLs
    url(r'^select2/', include('django_select2.urls')),

    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) +\
        staticfiles_urlpatterns()

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(r'^400/$', default_views.bad_request,
            kwargs={'exception': Exception('Bad Request!')}),

        url(r'^403/$', default_views.permission_denied,
            kwargs={'exception': Exception('Permission Denied')}),

        url(r'^404/$', default_views.page_not_found,
            kwargs={'exception': Exception('Page not Found')}),

        url(r'^500/$', default_views.server_error),
        ]
