from wastd.utils import ListResourceView, DetailResourceView
from .models import (
    Encounter,
    Area,
    Survey,
    SurveyMediaAttachment,
)
from .serializers_v2 import (
    EncounterSerializer,
    AreaSerializer,
    SurveySerializer,
    SurveyMediaAttachmentSerializer,
)


class EncounterListResource(ListResourceView):
    model = Encounter
    serializer = EncounterSerializer

    def get_queryset(self):
        # FIXME: permissions checking per object.
        return Encounter.objects.all(
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
