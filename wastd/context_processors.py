from django.conf import settings


def template_context(request):
    """Pass extra context variables to every template."""
    context = {
        "SITE_NAME": settings.SITE_NAME,
        "SITE_TITLE": settings.SITE_TITLE,
        "SITE_CODE": settings.SITE_CODE,
        "BIOSYS_TSC_URL": settings.BIOSYS_TSC_URL,
        "BIOSYS_UN": settings.BIOSYS_UN,
        "BIOSYS_PW": settings.BIOSYS_PW,
        "WASTD_RELEASE": settings.WASTD_RELEASE,
        "LEAFLET_CONFIG": settings.LEAFLET_CONFIG,
    }
    context.update(settings.STATIC_CONTEXT_VARS)
    return context
