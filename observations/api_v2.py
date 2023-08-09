from django.http import HttpResponseBadRequest
from wastd.utils import ListResourceView, DetailResourceView
from .models import (
    Area,
    Survey,
    SurveyMediaAttachment,
    Encounter,
    AnimalEncounter,
    TurtleNestEncounter,
    MediaAttachment,
    TurtleNestObservation,
    TurtleHatchlingEmergenceObservation,
    NestTagObservation,
)
from .serializers_v2 import (
    AreaSerializer,
    SurveySerializer,
    SurveyMediaAttachmentSerializer,
    EncounterSerializer,
    AnimalEncounterSerializer,
    TurtleNestEncounterSerializer,
    MediaAttachmentSerializer,
    TurtleNestObservationSerializer,
    TurtleHatchlingEmergenceObservationSerializer,
    NestTagObservationSerializer,
)


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


class EncounterListResource(ListResourceView):
    model = Encounter
    serializer = EncounterSerializer

    def get_queryset(self):
        # FIXME: permissions checking per object.
        return self.model.objects.all(
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


class AnimalEncounterListResource(EncounterListResource):
    model = AnimalEncounter
    serializer = AnimalEncounterSerializer


class AnimalEncounterDetailResource(EncounterDetailResource):
    model = AnimalEncounter
    serializer = AnimalEncounterSerializer


class TurtleNestEncounterListResource(EncounterListResource):
    model = TurtleNestEncounter
    serializer = TurtleNestEncounterSerializer


class TurtleNestEncounterDetailResource(EncounterDetailResource):
    model = TurtleNestEncounter
    serializer = TurtleNestEncounterSerializer


class ObservationListResource(ListResourceView):

    def dispatch(self, request, *args, **kwargs):
        if 'encounter_id' in request.GET and request.GET['encounter_id']:
            try:
                int(request.GET['encounter_id'])
            except:
                return HttpResponseBadRequest()
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()

        if 'encounter_id' in self.request.GET and self.request.GET['encounter_id']:
            queryset = queryset.filter(encounter__pk=int(self.request.GET['encounter_id']))

        return queryset


class MediaAttachmentListResource(ObservationListResource):
    model = MediaAttachment
    serializer = MediaAttachmentSerializer


class MediaAttachmentDetailResource(DetailResourceView):
    model = MediaAttachment
    serializer = MediaAttachmentSerializer


class TurtleNestObservationListResource(ObservationListResource):
    model = TurtleNestObservation
    serializer = TurtleNestObservationSerializer


class TurtleNestObservationDetailResource(DetailResourceView):
    model = TurtleNestObservation
    serializer = TurtleNestObservationSerializer


class TurtleHatchlingEmergenceObservationListResource(ObservationListResource):
    model = TurtleHatchlingEmergenceObservation
    serializer = TurtleHatchlingEmergenceObservationSerializer


class TurtleHatchlingEmergenceObservationDetailResource(DetailResourceView):
    model = TurtleHatchlingEmergenceObservation
    serializer = TurtleHatchlingEmergenceObservationSerializer


class NestTagObservationListResource(ObservationListResource):
    model = NestTagObservation
    serializer = NestTagObservationSerializer


class NestTagObservationDetailResource(DetailResourceView):
    model = NestTagObservation
    serializer = NestTagObservationSerializer
