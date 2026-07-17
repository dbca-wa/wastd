from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied


class ModuleAccessMiddleware:
    """Gate top-level business modules by per-user module access flags."""

    MODULE_RULES = {
        "wamtram2": "tagging",
        "marine_mammal_incidents": "marine_wildlife",
    }
    TRACKS_OBSERVATION_NAMES = (
        "turtlenest",
        "linetransect",
        "tracktally",
    )
    MARINE_OBSERVATION_NAMES = (
        "animalencounter",
        "disturbanceobservation",
    )
    SHARED_OBSERVATION_NAMES = (
        "encounter",
        "survey",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        required_module = self._required_module(request)
        if not required_module:
            return None

        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())

        if isinstance(required_module, tuple):
            has_access = any(request.user.has_module_access(module) for module in required_module)
        else:
            has_access = request.user.has_module_access(required_module)

        if not has_access:
            raise PermissionDenied("You do not have permission to access this module.")

        return None

    def _required_module(self, request):
        match = getattr(request, "resolver_match", None)
        if not match:
            return None

        if match.namespace in self.MODULE_RULES:
            return self.MODULE_RULES[match.namespace]

        if match.url_name == "map" or match.url_name == "strandings_geojson":
            return "marine_wildlife"

        if match.namespace != "observations" or not match.url_name:
            return None

        if match.url_name.startswith(self.TRACKS_OBSERVATION_NAMES):
            return "tracks_nests"
        if match.url_name.startswith(self.MARINE_OBSERVATION_NAMES):
            return "marine_wildlife"
        if match.url_name.startswith(self.SHARED_OBSERVATION_NAMES):
            return ("tracks_nests", "marine_wildlife")

        return None