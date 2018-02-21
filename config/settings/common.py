# -*- coding: utf-8 -*-
"""
Django settings for WAStD project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""
from __future__ import absolute_import, unicode_literals
import environ
from confy import env, database
from unipath import Path

import confy

try:
    confy.read_environment_file(".env")
except:
    pass

ROOT_DIR = environ.Path(__file__) - 3  # (wastd/config/settings/common.py - 3 = wastd/)
BASE_DIR = Path(__file__).ancestor(3)
APPS_DIR = ROOT_DIR.path('wastd')


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
    'grappelli',
    'django.contrib.admin',
)

THIRD_PARTY_APPS = (
    'django_extensions',            # shell_plus and others
    'crispy_forms',                 # Form layouts
    'floppyforms',                  # Floppyforms: Admin GIS widgets
    'easy_select2',                 # Select2 dropdowns
    'django_tables2',               # View mixins
    'django_filters',               # Form filters
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
    'reversion',                    # Version history
    'graphene_django',              # GraphQL API
    'rest_framework',               # API
    'rest_framework.authtoken',     # API auth via token
    'rest_framework_gis',           # API spatial fields
    'rest_framework_swagger',       # API docs
    'rest_framework_latex',         # API latex renderer
    # 'dynamic_rest',                 # Parameterised API queries

)

# Apps specific for this project go here.
LOCAL_APPS = (
    # custom users app
    'wastd.users.apps.UsersConfig',
    # Your stuff: custom apps go here
    'wastd.observations.apps.ObservationsConfig',
    'taxonomy.apps.TaxonomyConfig',
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# MIDDLEWARE CONFIGURATION
# ------------------------------------------------------------------------------
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'dpaw_utils.middleware.SSOLoginMiddleware',
)

# MIGRATIONS CONFIGURATION
# ------------------------------------------------------------------------------
MIGRATION_MODULES = {
    'sites': 'wastd.contrib.sites.migrations'
}


# CACHES
# ------------------------------------------------------------------------------
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': '{0}/{1}'.format(env('REDIS_URL', default='redis://127.0.0.1:6379'), 0),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'IGNORE_EXCEPTIONS': True,  # mimics memcache behavior.
                                        # http://niwinz.github.io/django-redis/latest/#_memcached_exceptions_behavior
        }
    }
}


# DEBUG
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env('DJANGO_DEBUG', default=False)
DEFAULT_USER_PASSWORD = env('DEFAULT_USER_PASSWORD', default='test123')

# FIXTURE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-FIXTURE_DIRS
FIXTURE_DIRS = (
    str(APPS_DIR.path('fixtures')),
)

# EMAIL CONFIGURATION
# ------------------------------------------------------------------------------
EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND',
                    default='django.core.mail.backends.smtp.EmailBackend')

# Email
EMAIL_HOST = env('EMAIL_HOST', default='smtp.corporateict.domain')
EMAIL_PORT = env('EMAIL_PORT', default=25)
DEFAULT_FROM_EMAIL = '"WA Strandings DB" <strandings-noreply@dpaw.wa.gov.au>'

# MANAGER CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = (
    ("Florian Mayer", 'Florian.Mayer@dpaw.wa.gov.au'),
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS

# DATABASE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {'default': database.config()}
DATABASES['default']['ATOMIC_REQUESTS'] = True


# GENERAL CONFIGURATION
# ------------------------------------------------------------------------------
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Australia/Perth'
# DATE_FORMAT = "Y-m-d"
# DATE_INPUT_FORMATS = [
#     '%Y-%m-%d',      # '2006-10-25'
#     '%Y-%m-%dZ',     # '2006-10-25Z' from WACensus via KMI GeoServer
#     '%m/%d/%Y',      # '10/25/2006'
#     '%m/%d/%y',
# ]      # '10/25/06'


# See: https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = 'en-us'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True

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
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
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

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = (
    str(APPS_DIR.path('static')),
)
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.CachedStaticFilesStorage'
# STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'


# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder'
)

# django-compressor
# ------------------------------------------------------------------------------
INSTALLED_APPS += ("compressor", )
COMPRESS_ROOT = STATIC_ROOT
COMPRESS_URL = STATIC_URL


# MEDIA CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(APPS_DIR('media'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = '/media/'

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


# Location of root django.contrib.admin URL, use {% url 'admin:index' %}
ADMIN_URL = "^admin/"


# Your common stuff: Below this line define 3rd party library settings

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
    # 'DEFAULT_PARSER_CLASSES': (
    # 'rest_framework_yaml.parsers.YAMLParser',
    # ),
    'DEFAULT_FILTER_BACKENDS': (
        # 'django_filters.rest_framework.DjangoFilterBackend',
        # 'rest_framework_gis.filters.InBBoxFilter',
        'rest_framework_filters.backends.DjangoFilterBackend',
    ),

    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework_gis.pagination.GeoJsonPagination',
    'PAGE_SIZE': 100,
}

# Shared Latex resources for DRF-latex
# http://drf-latex.readthedocs.io/en/latest/
LATEX_RESOURCES = str(APPS_DIR('templates/latex/common'))


# Grappelli admin theme
# ------------------------------------------------------------------------------
GRAPPELLI_ADMIN_TITLE = "WAStD Data Entry and Curation Portal"

# Django-filters
# ------------------------------------------------------------------------------
# Exclude help text unless specifically given
# FILTERS_HELP_TEXT_EXCLUDE = True
# FILTERS_HELP_TEXT_FILTER = False

# Leaflet maps
# ------------------------------------------------------------------------------
LEAFLET_CONFIG = {
    'DEFAULT_CENTER': (-25, 130),
    'DEFAULT_ZOOM': 5,
    'SCALE': 'metric',
    'MINIMAP': False,
    'PLUGINS': {
        # 'leaflet-tilelayer-geojson': {
        #     'css': [],
        #     'js': '//static.dpaw.wa.gov.au/static/libs/leaflet-tilelayer-geojson/1.0.4/TileLayer.GeoJSON.js',
        #     'auto-include': True,
        #     },
        # 'leaflet-markercluster': {
        #     'css': [
        #         '//static.dpaw.wa.gov.au/static/libs/leaflet.markercluster/1.0.0-rc.1.0/MarkerCluster.css',
        #         '//static.dpaw.wa.gov.au/static/libs/leaflet.markercluster/1.0.0-rc.1.0/MarkerCluster.Default.css', ],
        #     'js': '//static.dpaw.wa.gov.au/static/libs/leaflet.markercluster/1.0.0-rc.1.0/leaflet.markercluster.js',
        #     'auto-include': False,
        #     },
    },

    'TILES': [
        ('Aerial Image',
         '//server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
         {'attribution': 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'}),

        ('Place names',
         'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
         {'attribution': '&copy; <a href="//www.openstreetmap.org/copyright">OpenStreetMap</a>'}),

        ('Dirk Hartog mode',
         '//stamen-tiles-{s}.a.ssl.fastly.net/watercolor/{z}/{x}/{y}.{ext}',
         {'attribution': 'Map tiles by <a href="//stamen.com">Stamen Design</a>, <a href="//creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
          'subdomains': 'abcd',
          'minZoom': 1,
          'maxZoom': 16,
          'ext': 'png'}),

        ('Bathymetry',
         '//server.arcgisonline.com/ArcGIS/rest/services/Ocean_Basemap/MapServer/tile/{z}/{y}/{x}',
         {'attribution': 'Tiles &copy; Esri &mdash; Sources: GEBCO, NOAA, CHS, OSU, UNH, CSUMB, National Geographic, DeLorme, NAVTEQ, and Esri',
          'maxZoom': 13, }),

        ('Real time true colour',
         '//map1.vis.earthdata.nasa.gov/wmts-webmerc/MODIS_Terra_CorrectedReflectance_TrueColor/default/{time}/{tilematrixset}{maxZoom}/{z}/{y}/{x}.{format}',
         {'attribution': 'Imagery provided by services from the Global Imagery Browse Services (GIBS), operated by the NASA/GSFC/Earth Science Data and Information System (<a href="https://earthdata.nasa.gov">ESDIS</a>) with funding provided by NASA/HQ.',
          'bounds': [[-85.0511287776, -179.999999975], [85.0511287776, 179.999999975]],
          'minZoom': 1,
          'maxZoom': 9,
          'format': 'jpg',
          'time': '',
          'tilematrixset': 'GoogleMapsCompatible_Level'}),

        ('Real time false colour',
         '//map1.vis.earthdata.nasa.gov/wmts-webmerc/MODIS_Terra_CorrectedReflectance_Bands367/default/{time}/{tilematrixset}{maxZoom}/{z}/{y}/{x}.{format}',
         {'attribution': 'Imagery provided by services from the Global Imagery Browse Services (GIBS), operated by the NASA/GSFC/Earth Science Data and Information System (<a href="https://earthdata.nasa.gov">ESDIS</a>) with funding provided by NASA/HQ.',
          'bounds': [[-85.0511287776, -179.999999975], [85.0511287776, 179.999999975]],
          'minZoom': 1,
          'maxZoom': 9,
          'format': 'jpg',
          'time': '',
          'tilematrixset': 'GoogleMapsCompatible_Level'}),

        ('Light pollution',
         '//map1.vis.earthdata.nasa.gov/wmts-webmerc/VIIRS_CityLights_2012/default/{time}/{tilematrixset}{maxZoom}/{z}/{y}/{x}.{format}',
         {'attribution': 'Imagery provided by services from the Global Imagery Browse Services (GIBS), operated by the NASA/GSFC/Earth Science Data and Information System (<a href="https://earthdata.nasa.gov">ESDIS</a>) with funding provided by NASA/HQ.',
          'bounds': [[-85.0511287776, -179.999999975], [85.0511287776, 179.999999975]],
          'minZoom': 1,
          'maxZoom': 8,
          'format': 'jpg',
          'time': '',
          'tilematrixset': 'GoogleMapsCompatible_Level'}),
    ]
}


# Synctool
SYNCTOOL_API_TOKEN = env('SYNCTOOL_API_TOKEN', default='TOKEN')

# Phone number
PHONENUMBER_DB_FORMAT = 'INTERNATIONAL'

# Google Maps API key
GOOGLE_MAPS_API_KEY = env('GOOGLE_MAPS_API_KEY', default="not-set")

# Graphene-django
GRAPHENE = {
    'SCHEMA': 'wastd.schema.schema'
}


# Guardian permissions, django-polymorphic integration
GUARDIAN_GET_CONTENT_TYPE = 'polymorphic.contrib.guardian.get_polymorphic_base_content_type'
