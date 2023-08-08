from wastd.utils import ListResourceView, DetailResourceView
from .models import (
    Encounter,
    AnimalEncounter,
    TurtleNestEncounter,
    Area,
    Survey,
    SurveyMediaAttachment,
    MediaAttachment,
)
from .serializers_v2 import (
    EncounterSerializer,
    AreaSerializer,
    SurveySerializer,
    SurveyMediaAttachmentSerializer,
    MediaAttachmentSerializer,
    AnimalEncounterSerializer,
    TurtleNestEncounterSerializer,
)


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


class MediaAttachmentListResource(ListResourceView):
    model = MediaAttachment
    serializer = MediaAttachmentSerializer


class MediaAttachmentDetailResource(DetailResourceView):
    model = MediaAttachment
    serializer = MediaAttachmentSerializer
