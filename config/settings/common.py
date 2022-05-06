# -*- coding: utf-8 -*-
"""
Django settings for WAStD project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""
import os
import csv
import environ
# from confy import database, env
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from unipath import Path

env = environ.Env(
    # set casting, default value
    DATABASE_URL=(str, ''),
    DJANGO_DEBUG=(bool, False),
    SENTRY_DSN=(str, ''),
    DJANGO_SECRET_KEY=(str, 'changeme'),
    OFFLINE=(bool, False),
    DJANGO_PROFILING=(bool, False),
    INTERNAL_IPS=(list, 'localhost, 127.0.0.1, ::1'.split(',')),
    SITE_NAME=(str, "WA Sea Turtles and Strandings Database"),
    SITE_TITLE=(str, "WAStD"),
    SITE_CODE=(str, "WAStD"),
    DEFAULT_USER_PASSWORD=(str, 'test123'),
    DJANGO_ALLOWED_HOSTS=(str, "*, localhost"),
    DJANGO_EMAIL_BACKEND=(str, 'django.core.mail.backends.smtp.EmailBackend'),
    EMAIL_HOST=(str, 'smtp.lan.fyi'),
    EMAIL_PORT=(int, 25),
    DEFAULT_FROM_EMAIL=(str, 'no-reply@wastd.dbca.wa.gov.au'),
    ADMIN_USER=(int, 1),
    DJANGO_EMAIL_SUBJECT_PREFIX=(str, '[WAStD] '),
    MEMCACHED_URL=(str, 'memcached.default'),
    MEMCACHED_URL_SELECT2=(str, 'memcached.default'),
    WASTD_RELEASE=(str, '0.0.1'),
    ENABLE_AUTH2_GROUPS=(bool, True),
    LOCAL_USERGROUPS=(list, ["data viewer", "data curator", "data custodian", "data entry", "api"]),
    INTERNAL_EMAIL_SUFFIXES=(list, ["@dbca.wa.gov.au", ]),
    ALLOWED_EMAIL_SUFFIXES=(list, ["@dbca.wa.gov.au", ]),
)

ENABLE_AUTH2_GROUPS = env('ENABLE_AUTH2_GROUPS')
INTERNAL_EMAIL_SUFFIXES=env('INTERNAL_EMAIL_SUFFIXES')
LOCAL_USERGROUPS = env('LOCAL_USERGROUPS')
WASTD_RELEASE = env('WASTD_RELEASE')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))  # Populate env

ROOT_DIR = environ.Path(__file__) - 3  # (wastd/config/settings/common.py - 3 = wastd/)
BASE_DIR = Path(__file__).ancestor(3)
APPS_DIR = ROOT_DIR.path('wastd')

# DEBUG
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env('DJANGO_DEBUG', default=False)
OFFLINE = env('OFFLINE', default=False)
PROFILING = env('DJANGO_PROFILING', default=False)

ANIMALS_PK = env("ANIMALS_PK", default=20)
PLANTS_PK = env("PLANTS_PK", default=21)
INTERNAL_IPS = env("INTERNAL_IPS", default='localhost, 127.0.0.1, ::1'.split(','))

# APP CONFIGURATION
# ------------------------------------------------------------------------------
DJANGO_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.gis',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'grappelli.dashboard',
    'grappelli',
    'django.contrib.admin',
    'django.contrib.postgres',
)

THIRD_PARTY_APPS = (
    'django_extensions',            # shell_plus and others
    'environ',
    'fixture_magic',                # custom test fixtures
    'crispy_forms',                 # Form layouts
    'bootstrap4',                   # bootstrap4
    'floppyforms',                  # Floppyforms: Admin GIS widgets
    'easy_select2',                 # Select2 dropdowns
    'django_select2',               # Django select2 form helpers
    'ajax_select',                  # Ajax dropdowns
    'django_tables2',               # View mixins
    'django_filters',               # Form filters
    'mapwidgets',                   # Map widgets
    'allauth',                      # registration
    'allauth.account',              # registration
    'allauth.socialaccount',        # registration
    'adminactions',                 # extra admin trickery
    'djgeojson',                    # GeoJSON views
    'leaflet',                      # for djgeojson
    'phonenumber_field',            # Phone number field
    'django_fsm',                   # Transitions
    'django_fsm_log',               # Transition audit logs
    'fsm_admin',                    # Transitions in admin
    'reversion',                    # Version history, requires grappelli loaded
    # 'graphene_django',              # GraphQL API
    'rest_framework',               # API
    'rest_framework.authtoken',     # API auth via token
    'rest_framework_gis',           # API spatial fields
    'rest_framework_swagger',       # API docs
    'rest_framework_latex',         # API latex renderer
    'rest_framework_filters',
    # 'dynamic_rest',                 # Parameterised API queries
    'mptt',                         # Graph database: tree models
    'background_task',              # Job queue
    'export_download',              # listview exports
    'import_export',                # data import/export

    'gunicorn',                     # Web server
    # 'wms',                          # WMS server - fails on broken mapscript
    # 'test_utils',                    # Testing - fails on BS install
    # 'raven.contrib.django.raven_compat',  # Sentry logging Raven client
)

# Apps specific for this project go here.
LOCAL_APPS = (
    'wastd.users.apps.UsersConfig',
    'shared.apps.SharedConfig',
    'wastd.observations.apps.ObservationsConfig',
)

DEBUG_APPS = ('debug_toolbar',)
PROFILING_APPS = ('silk', )

# See: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

if DEBUG:
    INSTALLED_APPS += DEBUG_APPS
if PROFILING:
    INSTALLED_APPS += PROFILING_APPS


# SECRET CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key only used for development and testing.
SECRET_KEY = env('DJANGO_SECRET_KEY', default='c4)!ho4t^lsy0ozrnlqamjso@^n-ookiq)en=-pn#itkqj&xi6')

# MIDDLEWARE CONFIGURATION
# ------------------------------------------------------------------------------
MIDDLEWARE_FIRST = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
)

MIDDLEWARE_LAST = (
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'dbca_utils.middleware.SSOLoginMiddleware',
    'shared.middleware.SSOLoginMiddleware'
)


if DEBUG:
    MIDDLEWARE_FIRST += ('debug_toolbar.middleware.DebugToolbarMiddleware',)

if PROFILING:
    MIDDLEWARE_FIRST += ('silk.middleware.SilkyMiddleware',)

MIDDLEWARE = MIDDLEWARE_FIRST + MIDDLEWARE_LAST

CACHE_MIDDLEWARE_ALIAS = "default"
CACHE_MIDDLEWARE_SECONDS = 60

# MIGRATIONS CONFIGURATION
# ------------------------------------------------------------------------------
MIGRATION_MODULES = {
    'sites': 'wastd.contrib.sites.migrations'
}


# Django 3.2
# https://docs.djangoproject.com/en/3.2/releases/3.2/#customizing-type-of-auto-created-primary-keys
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# CACHES
# ------------------------------------------------------------------------------

# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         'LOCATION': '{0}/{1}'.format(env('REDIS_URL', default='redis://redis:6379'), 0),
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#             'IGNORE_EXCEPTIONS': True,
#         }
#     },
#     "select2": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         'LOCATION': '{0}/{1}'.format(env('REDIS_URL', default='redis://redis:6379'), 1),
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#             'IGNORE_EXCEPTIONS': True,
#         }
#     }
# }

# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
#         'LOCATION': env('MEMCACHED_URL'),
#     },
#      'select2': {
#         'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
#         'LOCATION': env('MEMCACHED_URL_SELECT2'),
#     }
# }

# CACHES = {
#     "default": {
#         # 'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
#         "BACKEND": 'django.core.cache.backends.filebased.FileBasedCache',
#         'LOCATION': ''
#     },
#     "select2": {
#         "BACKEND": "django.core.cache.backends.db.DatabaseCache",
#         'LOCATION': 'select2_cache_table'
#     }
# }

# https://github.com/django-pymemcache/django-pymemcache
# CACHES = {
#     'default': {
#         'BACKEND': 'djpymemcache.backend.PyMemcacheCache',
#         'LOCATION': [env('MEMCACHED_URL'),],
#     },
#     'select2': {
#         'BACKEND': 'djpymemcache.backend.PyMemcacheCache',
#         'LOCATION': [env('MEMCACHED_URL_SELECT2'),],
#     },
# }

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'default',
    },
    'select2': {
       'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'select2',
    },
}
SELECT2_CACHE_BACKEND = "select2"
# CACHE_PREFIX = 'select2_'

# Data upload request size
DATA_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 1024
DATA_UPLOAD_MAX_NUMBER_FIELDS = None

# Branding
# ------------------------------------------------------------------------------
# https://github.com/jakubroztocil/django-settings-export
SITE_NAME = env('SITE_NAME')
SITE_TITLE = env('SITE_TITLE')
SITE_CODE = env('SITE_CODE')


DEFAULT_USER_PASSWORD = env('DEFAULT_USER_PASSWORD')

ALLOWED_HOSTS = env('DJANGO_ALLOWED_HOSTS')

# CSV export via django_adminactions
ADMINACTIONS_CSV_OPTIONS_DEFAULT = {
    'date_format': 'Y-m-d',
    'datetime_format': 'Y-m-d G:i:s O',
    'time_format': 'G:i:s',
    'header': True,
    'quotechar': '"',
    'quoting': csv.QUOTE_ALL,
    'delimiter': ',',
    'escapechar': '\\',
}

# Debug toolbar
# ------------------------------------------------------------------------------
DEBUG_TOOLBAR_CONFIG = {
    'DISABLE_PANELS': ['debug_toolbar.panels.redirects.RedirectsPanel', ],
    'SHOW_TEMPLATE_CONTEXT': True,
}

# FIXTURE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-FIXTURE_DIRS
FIXTURE_DIRS = (str(APPS_DIR.path('fixtures')),)

# EMAIL CONFIGURATION
# ------------------------------------------------------------------------------
EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND')
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')
EMAIL_SUBJECT_PREFIX = env('DJANGO_EMAIL_SUBJECT_PREFIX')

# Sentry email settings
SERVER_EMAIL = DEFAULT_FROM_EMAIL
SENTRY_ADMINS = ("Florian.Mayer@dbca.wa.gov.au",)

# MANAGER CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = (("Florian Mayer", 'Florian.Mayer@dbca.wa.gov.au'),)

TSC_ADMIN_USER = env("ADMIN_USER")

# See: https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS

# DATABASE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {'default': env.db()}
DATABASES['default']['ATOMIC_REQUESTS'] = True


# GENERAL CONFIGURATION
# ------------------------------------------------------------------------------
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Australia/Perth'
DATE_FORMAT = 'Y-m-d'
DATETIME_FORMAT = 'Y-m-d G:i:s T'
DATE_INPUT_FORMATS = [
    '%d/%m/%Y',      # '25/10/2006'
    '%d/%m/%y',
    '%d-%m-%Y',
    '%d-%m-%Y',      # '25-10-2006'
    '%d %b %Y',
    '%d %b, %Y',
    '%d %B %Y',
    '%d %B, %Y',
    '%Y-%m-%d',      # '2006-10-25'
    '%Y/%m/%d',      # '2006/10/25'
    '%Y-%m-%dZ',     # '2006-10-25Z' from WACensus via KMI GeoServer
]
DATETIME_INPUT_FORMATS = [
    '%d/%m/%Y %H:%M',
    '%d/%m/%y %H:%M',
    '%d-%m-%Y %H:%M',
    '%d-%m-%y %H:%M',
]


# See: https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = 'en-us'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = False

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True

# TEMPLATE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        'DIRS': [str(APPS_DIR.path('templates')), ],
        'OPTIONS': {
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
            'debug': DEBUG,
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ]),
            ],
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'django_settings_export.settings_export',
            ],
        },
    },
]

# See: http://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# STATIC FILE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(ROOT_DIR('staticfiles'))
if not os.path.exists(STATIC_ROOT):
    os.mkdir(STATIC_ROOT)

# http://whitenoise.evans.io/en/stable/django.html#WHITENOISE_ROOT
WHITENOISE_ROOT = STATIC_ROOT

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'
# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = (str(APPS_DIR.path('static')),)
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
# STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.CachedStaticFilesStorage'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'


# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder'
)


# MEDIA CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(ROOT_DIR('media'))
if not os.path.exists(MEDIA_ROOT):
    os.mkdir(MEDIA_ROOT)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = '/media/'


# django-compressor
# ------------------------------------------------------------------------------
# INSTALLED_APPS += ("compressor", )
COMPRESS_ROOT = STATIC_ROOT
COMPRESS_URL = STATIC_URL

# http://whitenoise.evans.io/en/stable/django.html#django-compressor
# https://django-compressor.readthedocs.io/en/latest/usage/#offline-compression
# COMPRESS_OFFLINE=True


# URL Configuration
# ------------------------------------------------------------------------------
ROOT_URLCONF = 'config.urls'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = 'config.wsgi.application'

# AUTHENTICATION CONFIGURATION
# ------------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

# Some really nice defaults
ACCOUNT_AUTHENTICATION_METHOD = 'username'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'

ACCOUNT_ALLOW_REGISTRATION = env('DJANGO_ACCOUNT_ALLOW_REGISTRATION', default=True)
ACCOUNT_ADAPTER = 'wastd.users.adapters.AccountAdapter'
SOCIALACCOUNT_ADAPTER = 'wastd.users.adapters.SocialAccountAdapter'

# Custom user app defaults
# Select the correct user model
AUTH_USER_MODEL = 'users.User'
LOGIN_REDIRECT_URL = 'users:redirect'
LOGIN_URL = 'account_login'

# SLUGLIFIER
AUTOSLUG_SLUGIFY_FUNCTION = 'slugify.slugify'

# Session management
# http://niwinz.github.io/django-redis/latest/#_configure_as_cache_backend
# SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
SESSION_CACHE_ALIAS = "default"
# SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'

# Location of root django.contrib.admin URL, use {% url 'admin:index' %}
ADMIN_URL = "admin/"

# API: django-restframework
# ------------------------------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),

    # http://www.django-rest-framework.org/api-guide/permissions/
    'DEFAULT_PERMISSION_CLASSES': [
        # 'rest_framework.permissions.IsAuthenticated',
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
        'rest_framework.permissions.IsAdminUser',
    ],
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework.renderers.JSONRenderer',
        'rest_framework_jsonp.renderers.JSONPRenderer',
        # 'rest_framework_csv.renderers.CSVRenderer',
        'rest_framework_yaml.renderers.YAMLRenderer',
        'rest_framework_latex.renderers.LatexRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': [
        # 'rest_framework_yaml.parsers.YAMLParser',
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_FILTER_BACKENDS': (
        # 'django_filters.rest_framework.DjangoFilterBackend',
        # 'rest_framework_gis.filters.InBBoxFilter',
        'rest_framework_filters.backends.RestFrameworkFilterBackend',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100,
    'HTML_SELECT_CUTOFF': 100,
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}

# PROXY_PAGINATION_PARAM = 'pager'
# PROXY_PAGINATION_DEFAULT = 'rest_framework.pagination.LimitOffsetPagination'
# PROXY_PAGINATION_MAPPING = {
#     'lim': 'rest_framework.pagination.LimitOffsetPagination',

#     # FieldError at /api/1/taxon/: Cannot resolve keyword 'created' into field.
#     'cur': 'rest_framework.pagination.CursorPagination',

#     # does nothing
#     'geo': 'rest_framework_gis.pagination.GeoJsonPagination',

#     # AttributeError: module 'rest_framework.viewsets' has no attribute 'ModelViewSet'.
#     # 'geolim': 'shared.api.MyGeoJsonPagination',

#     # AttributeError: 'NoneType' object has no attribute 'rsplit'.
#     # 'none': None
# }

# Shared Latex resources for DRF-latex
# http://drf-latex.readthedocs.io/en/latest/
LATEX_RESOURCES = str(APPS_DIR('templates/latex/common'))


# Grappelli admin theme
# ------------------------------------------------------------------------------
GRAPPELLI_ADMIN_TITLE = "Data Entry and Curation Portal"

# Django-filters
# ------------------------------------------------------------------------------
# Exclude help text unless specifically given
# FILTERS_HELP_TEXT_EXCLUDE = True
# FILTERS_HELP_TEXT_FILTER = False

# Biosys
# ------------------------------------------------------------------------------
BIOSYS_TSC_URL = env(
    "BIOSYS_TSC",
    default="https://biosys-uat.dbca.wa.gov.au/api/record/?project_id=61&name_id=")
BIOSYS_UN = env("BIOSYS_UN", default="")
BIOSYS_PW = env("BIOSYS_PW", default="")

# Leaflet maps
# ------------------------------------------------------------------------------
LEAFLET_CONFIG = {
    'SPATIAL_EXTENT': (-180, -90, 180, 90),
    'DEFAULT_CENTER': (-25, 120),
    'DEFAULT_ZOOM': 4,
    'SCALE': 'metric',
    'MINIMAP': False,
    # 'FORCE_IMAGE_PATH': True,
    # To take advantage of browser caching, the assets below are included separately
    # through templates shared/leaflet_{css, js}.html with SRI tags.
    'PLUGINS': {
        'forms': {'auto-include': True},
        'markers': {
            # 'css': 'css/leaflet.awesome-markers.css',
            # 'js': 'js/leaflet.awesome-markers.min.js',
            'auto-include': True
        },
        'label': {
            # 'css': 'css/leaflet.label.css',
            # 'js': 'js/leaflet.label.js',
            'auto-include': True
        },
        'geocoder': {
            # 'css': 'css/Control.Geocoder.css',
            # 'js': 'js/Control.Geocoder.min.js',
            'auto-include': True
        },
        'fullscreen': {
            # 'css': 'css/Control.FullScreen.css',
            # 'js': 'js/Control.FullScreen.min.js',
            'auto-include': True
        },
        'markercluster': {
            # 'css': ['css/MarkerCluster.css', 'css/MarkerCluster.Default.css'],
            # 'js': 'js/leaflet.markercluster.js',
            'auto-include': True
        },
        'tilelayer': {
            # 'js': 'js/TileLayer.GeoJSON.min.js',
            'auto-include': True
        },
    },
    'TILES': [
        ('Aerial Image',
         '//server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
         {'attribution': 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'}),  # noqa

        ('Place names',
         'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
         {'attribution': '&copy; <a href="//www.openstreetmap.org/copyright">OpenStreetMap</a>'}),

        ('Dirk Hartog mode',
         '//stamen-tiles-{s}.a.ssl.fastly.net/watercolor/{z}/{x}/{y}.{ext}',
         {'attribution': 'Map tiles by <a href="//stamen.com">Stamen Design</a>, <a href="//creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',   # noqa
          'subdomains': 'abcd',
          'minZoom': 1,
          'maxZoom': 16,
          'ext': 'png'}),

        ('Bathymetry',
         '//server.arcgisonline.com/ArcGIS/rest/services/Ocean_Basemap/MapServer/tile/{z}/{y}/{x}',
         {'attribution': 'Tiles &copy; Esri &mdash; Sources: GEBCO, NOAA, CHS, OSU, UNH, CSUMB, National Geographic, DeLorme, NAVTEQ, and Esri',  # noqa
          'maxZoom': 13, }),

        ('Real time true colour',
         '//map1.vis.earthdata.nasa.gov/wmts-webmerc/MODIS_Terra_CorrectedReflectance_TrueColor/default/{time}/{tilematrixset}{maxZoom}/{z}/{y}/{x}.{format}',  # noqa
         {'attribution': 'Imagery provided by services from the Global Imagery Browse Services (GIBS), operated by the NASA/GSFC/Earth Science Data and Information System (<a href="https://earthdata.nasa.gov">ESDIS</a>) with funding provided by NASA/HQ.',  # noqa
          'bounds': [[-85.0511287776, -179.999999975], [85.0511287776, 179.999999975]],
          'minZoom': 1,
          'maxZoom': 9,
          'format': 'jpg',
          'time': '',
          'tilematrixset': 'GoogleMapsCompatible_Level'}),

        ('Real time false colour',
         '//map1.vis.earthdata.nasa.gov/wmts-webmerc/MODIS_Terra_CorrectedReflectance_Bands367/default/{time}/{tilematrixset}{maxZoom}/{z}/{y}/{x}.{format}',  # noqa
         {'attribution': 'Imagery provided by services from the Global Imagery Browse Services (GIBS), operated by the NASA/GSFC/Earth Science Data and Information System (<a href="https://earthdata.nasa.gov">ESDIS</a>) with funding provided by NASA/HQ.',  # noqa
          'bounds': [[-85.0511287776, -179.999999975], [85.0511287776, 179.999999975]],
          'minZoom': 1,
          'maxZoom': 9,
          'format': 'jpg',
          'time': '',
          'tilematrixset': 'GoogleMapsCompatible_Level'}),

        ('Light pollution',
         '//map1.vis.earthdata.nasa.gov/wmts-webmerc/VIIRS_CityLights_2012/default/{time}/{tilematrixset}{maxZoom}/{z}/{y}/{x}.{format}',  # noqa
         {'attribution': 'Imagery provided by services from the Global Imagery Browse Services (GIBS), operated by the NASA/GSFC/Earth Science Data and Information System (<a href="https://earthdata.nasa.gov">ESDIS</a>) with funding provided by NASA/HQ.',  # noqa
          'bounds': [[-85.0511287776, -179.999999975], [85.0511287776, 179.999999975]],
          'minZoom': 1,
          'maxZoom': 8,
          'format': 'jpg',
          'time': '',
          'tilematrixset': 'GoogleMapsCompatible_Level'}),
    ],
    'OVERLAYS': [
        # ('State Map Base 250K', 'https://kmi.dbca.wa.gov.au/geoserver/cddp/wms',
        # {'attribution': '&copy; IGN', 'layers': 'cddp:state_map_base', 'format': 'image/png', 'transparent': 'true', }),
    ]

}
# https://stackoverflow.com/questions/43608919/html-offline-map-with-local-tiles-via-leaflet
if OFFLINE:
    LEAFLET_CONFIG['TILES'] = [
        ('Place Names',
        env("OSM_TILESERVER", default="//127.0.0.1:32768") + '/styles/osm-bright/{z}/{x}/{y}.png',
        {'attribution': 'OpenMapTiles', 'maxZoom': 16, }),
        ('Aerial Image',
         '//server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
         {'attribution': 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'}),  # noqa
    ]

# Synctool
SYNCTOOL_API_TOKEN = env('SYNCTOOL_API_TOKEN', default='TOKEN')

# Phone number
PHONENUMBER_DB_FORMAT = 'INTERNATIONAL'

# Google Maps API key
GOOGLE_MAPS_API_KEY = env('GOOGLE_MAPS_API_KEY', default="not-set")

# Graphene-django
GRAPHENE = {
    'SCHEMA': 'api.schema'
}


# Guardian permissions, django-polymorphic integration
GUARDIAN_GET_CONTENT_TYPE = 'polymorphic.contrib.guardian.get_polymorphic_base_content_type'

# Background tasks
# ------------------------------------------------------------------------------
BACKGROUND_TASK_RUN_ASYNC = True
MAX_ATTEMPTS = 5
MAX_RUN_TIME = 7200  # 2h

# Django-silk performance monitoring
# ------------------------------------------------------------------------------
# https://github.com/jazzband/django-silk#limiting-requestresponse-data
SILKY_MAX_RECORDED_REQUESTS = 100
# https://github.com/jazzband/django-silk#meta-profiling
SILKY_META = True
# https://github.com/jazzband/django-silk#profiling
SILKY_PYTHON_PROFILER = True
SILKY_PYTHON_PROFILER_BINARY = True

# Testing
# ------------------------------------------------------------------------------


# Pandoc
# Addressing a build error on GitHub Actions "No pandoc was found"
os.environ.setdefault('PYPANDOC_PANDOC', '/usr/bin/pandoc')

# Data
# ------------------------------------------------------------------------------
# Local cache of downloaded ODK data
DATA_ROOT = os.path.join(MEDIA_ROOT, 'data')
if not os.path.exists(DATA_ROOT):
    os.mkdir(DATA_ROOT)

# LOGGING CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#logging
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOG_ROOT = str(ROOT_DIR('logs'))
if not os.path.exists(LOG_ROOT):
    os.mkdir(LOG_ROOT)

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
        'sentry': {
            'level': 'WARNING',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
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
        # 'file': {
        #     'level': 'DEBUG',
        #     'class': 'logging.handlers.RotatingFileHandler',
        #     'filename': str(ROOT_DIR.path('logs', 'wastd.log')),
        #     'formatter': 'verbose',
        #     'maxBytes': 16777216
        # },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console', 'sentry'],
            'level': 'INFO',
            'propagate': True
        },
        'django.security.DisallowedHost': {
            'level': 'INFO',
            'handlers': ['console', 'sentry'],
            'propagate': True
        },
        'django': {
            'level': 'INFO',
            'handlers': ['console', 'sentry'],
            'propagate': True
        },
        "background_task": {
            'level': 'INFO',
            'handlers': ['console', 'sentry'],
            'propagate': True,
        },
        "silk": {
            'level': 'INFO',
            'handlers': ['console', 'sentry'],
            'propagate': True,
        },
        'shared': {
            'level': 'DEBUG',
            'handlers': ['console', 'sentry'],
            'propagate': True,
        },
        'wastd': {
            'level': 'DEBUG',
            'handlers': ['console', 'sentry'],
            'propagate': True,
        },
    }
}


# Grappelli admin
GRAPPELLI_INDEX_DASHBOARD = 'shared.dashboard.AdminDashboard'
# GRAPPELLI_ADMIN_TITLE = "Data Curation Portal"

# Error reporting
if env('SENTRY_DSN'):
    sentry_sdk.init(
        env('SENTRY_DSN'),
        integrations=[DjangoIntegration()],
        release="wastd@{0}".format(env("WASTD_RELEASE"))
    )

SETTINGS_EXPORT = [
    'SITE_NAME',
    'SITE_TITLE',
    'SITE_CODE',
    'BIOSYS_TSC_URL',
    'BIOSYS_UN',
    'BIOSYS_PW',
    'OFFLINE',
    'WASTD_RELEASE',
    'DATA_ROOT'
]
