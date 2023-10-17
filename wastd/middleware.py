from django.http import HttpResponse, HttpResponseServerError
import logging
from django.conf import settings
if settings.DEBUG:
    from debug_toolbar.panels import Panel


LOGGER = logging.getLogger("turtles")


class HealthCheckMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "GET":
            if request.path == "/readiness":
                return self.readiness(request)
            elif request.path == "/liveness":
                return self.liveness(request)
        return self.get_response(request)

    def liveness(self, request):
        """Returns that the server is alive.
        """
        return HttpResponse("OK")

    def readiness(self, request):
        """Connect to each database and do a generic standard SQL query
        that doesn't write any data and doesn't depend on any tables
        being present.
        """
        try:
            from django.db import connections
            cursor = connections["default"].cursor()
            cursor.execute("SELECT 1;")
            row = cursor.fetchone()
            if row is None:
                return HttpResponseServerError("db: invalid response")
        except Exception as e:
            LOGGER.exception(e)
            return HttpResponseServerError("db: cannot connect to database.")

        return HttpResponse("OK")

if settings.DEBUG:
    #Create a debug panel to catch file downloads, allows profiling 
    #from https://stackoverflow.com/a/74223126
    class FileInterceptsPanel(Panel):
        has_content = False
        title = 'Intercept files'

        def process_request(self, request):
            """If the response contains a file, replace it by a dummy response"""
            response = super().process_request(request)
            response_is_file = ...  # use whatever test suits your case
            if response_is_file:
                response = HttpResponse('<body>debug file response</body>')
            return response

from dbca_utils.middleware import SSOLoginMiddleware

class CustomSSOLoginMiddleware(SSOLoginMiddleware):

    def process_request(self, request):
        # Bypass middleware for API endpoints
        if request.path.startswith('/observations/dbdump/'):
            return

        # Call the original process_request method for non-API requests
        return super().process_request(request)
