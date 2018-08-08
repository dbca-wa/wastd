# -*- coding: utf-8 -*-
"""
Local settings file.

- Run in Debug mode
- Use console backend for emails
- Add Django Debug Toolbar
- Add django-extensions as app
"""

from .common import *  # noqa
import socket
import os
from confy import env

# DEBUG
# ------------------------------------------------------------------------------
DEBUG = True
ALLOWED_HOSTS = ["localhost", ]


# Mail settings
# ------------------------------------------------------------------------------

EMAIL_PORT = 1025

EMAIL_HOST = 'localhost'
EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND',
                    default='django.core.mail.backends.console.EmailBackend')


# CACHING
# ------------------------------------------------------------------------------
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
#         'LOCATION': ''
#     }
# }

# Debug apps: django-debug-toolbar
# ------------------------------------------------------------------------------
# MW = (
#     'debug_toolbar.middleware.DebugToolbarMiddleware',
#     'silk.middleware.SilkyMiddleware',
# )
# MIDDLEWARE_CLASSES += MW
# MIDDLEWARE += MW
INSTALLED_APPS += ('debug_toolbar', )

INTERNAL_IPS = ['127.0.0.1', '10.0.2.2', ]
# tricks to have debug toolbar when developing with docker
if os.environ.get('USE_DOCKER') == 'yes':
    ip = socket.gethostbyname(socket.gethostname())
    INTERNAL_IPS += [ip[:-1] + "1"]

DEBUG_TOOLBAR_CONFIG = {
    'DISABLE_PANELS': [
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ],
    'SHOW_TEMPLATE_CONTEXT': True,
}
