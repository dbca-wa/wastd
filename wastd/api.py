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
from rest_framework_gis.filters import InBBoxFilter


logger = logging.getLogger(__name__)


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
