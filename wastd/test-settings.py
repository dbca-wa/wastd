import logging
from .settings import *
import django
django.setup()

# Modify project settings to speed up unit tests.
logging.disable(logging.CRITICAL)
DEBUG = False

# Use the PostgreSQL database for tests
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'test_db',
        'USER': 'test_user',
        'PASSWORD': 'test_password',
        'HOST': 'localhost',
        'PORT': '5431', 
    }
}

# Custom Database Creation class to avoid creating and destroying test database
from django.db.backends.postgresql.creation import DatabaseCreation

class NoopDatabaseCreation(DatabaseCreation):
    def _create_test_db(self, *args, **kwargs):
        pass

    def _destroy_test_db(self, *args, **kwargs):
        pass

# Ensure Django uses custom DatabaseCreation class in test environment
from django.db import connection
connection.settings_dict['TEST'] = {
    'NAME': 'test_db',
    'MIRROR': 'default',
}
connection.creation_class = NoopDatabaseCreation

TEMPLATES[0]['OPTIONS'] = {
    'debug': False,
    "libraries": {
        "proper_paginate": "wastd.templatetags.proper_paginate",
        "url_replace": "wastd.templatetags.url_replace",
        "dict_filter": "wastd.templatetags.dict_filter",
    },
    'context_processors': [
        'django.contrib.auth.context_processors.auth',
        'django.template.context_processors.media',
        'django.template.context_processors.static',
        'django.template.context_processors.request',
        'django.template.context_processors.csrf',
        'django.contrib.messages.context_processors.messages',
        'wastd.context_processors.template_context',
    ],
}

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Database routers (if any)
DATABASE_ROUTERS = ["wamtram2.routers.Wamtram2Router"]

# Use the Django FSM log to ignore models
DJANGO_FSM_LOG_IGNORED_MODELS = []

# Static files (CSS, JavaScript, Images)
# Use simpler storage backend for tests
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
