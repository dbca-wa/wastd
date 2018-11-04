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


INTERNAL_IPS = ['127.0.0.1', '10.0.2.2', ]
# tricks to have debug toolbar when developing with docker
if os.environ.get('USE_DOCKER') == 'yes':
    ip = socket.gethostbyname(socket.gethostname())
    INTERNAL_IPS += [ip[:-1] + "1"]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'verbose': {
            'format': '%(asctime)-.19s [%(levelname)s]  %(message)s'
        },
        'simple': {
            'format': '[%(levelname)s] %(message)s',
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'WARNING',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(ROOT_DIR.path('logs', 'wastd.log')),
            'formatter': 'verbose',
            'maxBytes': 16777216
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True
        },
        'django.security.DisallowedHost': {
            'level': 'INFO',
            'handlers': ['console', 'file'],
            'propagate': True
        },
        'django': {
            'level': 'INFO',
            'handlers': ['console', 'file'],
            'propagate': True
        },
        "background_task": {
            'level': 'INFO',
            'handlers': ['console', 'file'],
            'propagate': True,
        },
        "silk": {
            'level': 'INFO',
            'handlers': ['console', 'file'],
            'propagate': True,
        },
        'wastd': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
            'propagate': True,
        },
        'shared': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
            'propagate': True,
        },
        'taxonomy': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
            'propagate': True,
        },
        'conservation': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
            'propagate': True,
        },
        'occurrence': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
            'propagate': True,
        },
    }
}
