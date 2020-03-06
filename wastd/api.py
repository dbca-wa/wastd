# -*- coding: utf-8 -*-
"""The WAStD API.

* Encouter and subclasses: AnimalEncounter, TurtleNestEncounter
* Encounter Inlines: Observation subclasses
* Separate TagObservation serializer to retrieve a Tag history
* Taxonomic names

This API outputs:

* Interactive HTML API
* CSV
* JSONP
* Latex (coming soon)

This API is built using:

* djangorestframework
* `djangorestframework-gis <https://github.com/djangonauts/django-rest-framework-gis>`_
* djangorestframework-csv
* `djangorestframework-yaml <http://www.django-rest-framework.org/api-guide/renderers/#yaml>`_ (TODO support geo field)
* djangorestframework-jsonp
* django-rest-polymorphic <https://github.com/apirobot/django-rest-polymorphic>
* django-url-filter
* dynamic-rest (not used)
* rest-framework-latex
* markdown
* django-filter
* django-rest-swagger
* coreapi
* coreapi-cli (complementary CLI for coreapi)
"""
import logging
from django.template import Context, Template
from rest_framework import routers, serializers, status, viewsets
from rest_framework.response import Response as RestResponse
from rest_framework_gis.filters import InBBoxFilter

from wastd.users.models import User

logger = logging.getLogger(__name__)
router = routers.DefaultRouter()


class InBBoxHTMLMixin:
    """Mixin for bbox search."""

    template = Template("""
    {% load i18n %}
    <style type="text/css">
    # geofilter input[type="text"]{
        width: 100px;
    }
    </style>
    <h2>{% trans "Limit results to area" %}</h2>
    <form id="geofilter" action="" method="get">

        <div class="form-group row">
            <div class="col-md-2"></div>
            <div class="col-md-2">
            <div class="controls">
            <input type="text" class="form-control" id="gf-north" placeholder="North">
            </div>
            </div>
        </div>

        <div class="form-group row">
            <div class="col-md-2">
            <div class="controls">
            <input type="text" class="form-control" id="gf-west" placeholder="West">
            </div>
            </div>

            <div class="col-md-2"></div>
            <div class="col-md-2">
            <div class="controls">
            <input type="text" class="form-control" id="gf-east" placeholder="East">
            </div>
            </div>
        </div>

        <div class="form-group row">
            <div class="col-md-2"></div>
            <div class="col-md-2">
            <div class="controls">
            <input type="text" class="form-control" id="gf-south" placeholder="South">
            </div>
            </div>
        </div>

        <input id="gf-result" type="hidden" name="{{bbox_param}}">
        <button type="submit" class="btn btn-primary">{% trans "Submit" %}
        </button>
    </form>
    <script language="JavaScript">
    (function() {
        document.getElementById("geofilter").onsubmit = function(){
            var result = document.getElementById("gf-result");
            var box = [
                document.getElementById("gf-south").value,
                document.getElementById("gf-west").value,
                document.getElementById("gf-north").value,
                document.getElementById("gf-east").value
            ];
            if(!box.every(function(i){ return i.length }))
                return false;
            result.value = box.join(",");
        }
    })();
    </script>
    """)

    def to_html(self, request, queryset, view):
        """Representation as HTML."""
        return self.template.render(Context({"bbox_param": self.bbox_param}))


class CustomBBoxFilter(InBBoxHTMLMixin, InBBoxFilter):
    """Custom BBox filter."""

    bbox_param = "in_bbox"


class UserSerializer(serializers.ModelSerializer):
    """User serializer."""

    class Meta:
        """Class options."""

        model = User
        fields = ("pk", "username", "name", "nickname", "aliases", "role", "email", "phone", )


class FastUserSerializer(serializers.ModelSerializer):
    """Minimal User serializer."""

    class Meta:
        """Class options."""

        model = User
        fields = ("pk", "username", "name",)


# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    """User view set."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    uid_field = "username"
    model = User

    def create_one(self, data):
        """POST: Create or update exactly one model instance."""
        from wastd.observations.utils import lowersnake
        un = lowersnake(data["name"])

        obj, created = self.model.objects.get_or_create(username=un, defaults=data)
        if not created:
            self.model.objects.filter(username=un).update(**data)

        verb = "Created" if created else "Updated"
        st = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        msg = "[API][UserViewSet][create_one] {0} {1}".format(verb, obj.__str__())
        content = {"id": obj.id, "msg": msg}
        logger.info(msg)

        return RestResponse(content, status=st)

    def create(self, request):
        """POST: Create or update one or many model instances.

        request.data must be:

        * a GeoJSON feature property dict, or
        * a list of GeoJSON feature property dicts.
        """
        # pdb.set_trace()
        if "name" in request.data:
            res = self.create_one(request.data)
            return res
        elif isinstance(request.data, list) and "name" in request.data[1]:
            res = [self.create_one(data) for data in request.data]
            return RestResponse(request.data, status=status.HTTP_200_OK)
        else:
            return RestResponse(request.data, status=status.HTTP_400_BAD_REQUEST)


router.register(r"users", UserViewSet)
