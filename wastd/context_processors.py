from django.conf import settings


def template_context(request):
    """Pass extra context variables to every template. Used by webtemplate-dbca base template.
    """
    context = {
        "page_title": settings.SITE_TITLE,
        "site_title": settings.SITE_TITLE,
        "site_acronym": settings.SITE_CODE,
        "APPLICATION_VERSION_NO": settings.VERSION_NO,
        "mapproxy_url": settings.MAPPROXY_URL,
    }
    return context
