import dj_database_url
import os
from pathlib import Path
import sys
from zoneinfo import ZoneInfo

# Build paths inside the project like this: os.path.join(BASE_DIR, 'subdir')
BASE_DIR = Path(__file__).resolve().parent.parent


# Settings defined in environment variables.
DEBUG = os.environ.get("DEBUG", False) == "True"
SECRET_KEY = os.environ.get("SECRET_KEY", "PlaceholderSecretKey")
if not DEBUG:
    ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")
else:
    ALLOWED_HOSTS = ["*"]
INTERNAL_IPS = ["127.0.0.1", "::1"]
ROOT_URLCONF = "wastd.urls"
WSGI_APPLICATION = "wastd.wsgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
# This is required to add context variables to all templates:
STATIC_CONTEXT_VARS = {}
FIXTURE_DIRS = [os.path.join(BASE_DIR, "wastd", "fixtures")]

# Assume Azure blob storage is used for media uploads, unless explicitly set as local storage.
LOCAL_MEDIA_STORAGE = os.environ.get("LOCAL_MEDIA_STORAGE", False)
if LOCAL_MEDIA_STORAGE:
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
else:
    DEFAULT_FILE_STORAGE = 'storages.backends.azure_storage.AzureStorage'
    AZURE_ACCOUNT_NAME = os.environ.get('AZURE_ACCOUNT_NAME', 'name')
    AZURE_ACCOUNT_KEY = os.environ.get('AZURE_ACCOUNT_KEY', 'key')
    AZURE_CONTAINER = os.environ.get('AZURE_CONTAINER', 'container')
    AZURE_URL_EXPIRATION_SECS = os.environ.get('AZURE_URL_EXPIRATION_SECS', 3600)  # Default one hour.



# Application settings
INSTALLED_APPS = [
    "whitenoise.runserver_nostatic",
    "polymorphic",  # Before django.contrib.contenttypes
    "django.contrib.contenttypes",
    "grappelli.dashboard",
    "grappelli",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.gis",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "django_fsm",
    "django_fsm_log",
    "fsm_admin",
    "reversion",
    'mapwidgets',
    "leaflet",
    "phonenumber_field",
    "crispy_forms",
    "bootstrap4",
    "bootstrap_pagination",
    "webtemplate_dbca",
    "django_filters",
    "export_download",
    "django_tables2",
    "django_select2",
    "easy_select2",
    "djgeojson",
    "import_export",
    #'rest_framework',
    # Local apps
    "users",
    "observations",
    "wamtram",  # Legacy WAMTRAM database
    "turtle_tags",
    "marine_mammal_incidents"
]
MIDDLEWARE = [
    "wastd.middleware.HealthCheckMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "reversion.middleware.RevisionMiddleware",
    "dbca_utils.middleware.SSOLoginMiddleware",
]

if DEBUG:
    # Application settings
    INSTALLED_APPS = INSTALLED_APPS + [
        "debug_toolbar",
    ]
    #need to redefined as the order is important for the debug toolbar
    MIDDLEWARE = [
        "wastd.middleware.HealthCheckMiddleware",
        "django.middleware.security.SecurityMiddleware",
        "whitenoise.middleware.WhiteNoiseMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "debug_toolbar.middleware.DebugToolbarMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
        "reversion.middleware.RevisionMiddleware",
        "dbca_utils.middleware.SSOLoginMiddleware",
        
    ]

    DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.history.HistoryPanel',
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
        'debug_toolbar.panels.profiling.ProfilingPanel',
        "wastd.middleware.FileInterceptsPanel"
    ]
    DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.history.HistoryPanel',
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
        'debug_toolbar.panels.profiling.ProfilingPanel',
        "wastd.middleware.FileInterceptsPanel"
    ]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "wastd", "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "debug": DEBUG,
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.template.context_processors.request",
                "django.template.context_processors.csrf",
                "django.contrib.messages.context_processors.messages",
                "wastd.context_processors.template_context",
            ],
        },
    },
]

MAP_WIDGETS = {
    "MapboxPointFieldWidget": {
        "access_token": os.environ.get("MAPBOX_TOKEN", ""),
        "markerFitZoom": 12,
        "mapOptions": {
            "animate": True,
            "zoom": 10,
            "center": (-31.996226, 115.883947),
            "scrollZoom": True,
        },
        "geocoderOptions": {
            "zoom": 7,
            "countries": "au"
        }
    }
}

#REST_FRAMEWORK = {
#    'DEFAULT_PERMISSION_CLASSES': [
#        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
#    ],
#    'DEFAULT_RENDERER_CLASSES': [
#        'rest_framework.renderers.JSONRenderer',
#    ]
#}
IMPORT_EXPORT_SKIP_ADMIN_CONFIRM=True

# Use the customised User model
AUTH_USER_MODEL = "users.User"
ADMIN_USER = os.environ.get("ADMIN_USER_ID", 1)
ENABLE_AUTH2_GROUPS = os.environ.get("ENABLE_AUTH2_GROUPS", False)
LOCAL_USERGROUPS = [
    "data viewer",
    "data curator",
    "data custodian",
    "data entry",
    "api",
]
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'

# Branding
SITE_NAME = os.environ.get("SITE_NAME", "Turtles Database")
SITE_TITLE = os.environ.get("SITE_TITLE", "Turtles Database")
SITE_CODE = os.environ.get("SITE_CODE", "Turtles")
VERSION_NO = "1.0.8"


# Database configuration
DATABASES = {
    # Defined in DATABASE_URL env variable.
    "default": dj_database_url.config(),
    "wamtram": {
        'ENGINE': os.environ.get('DB_ENGINE', 'mssql'),
        'HOST': os.environ.get('DB_HOST', 'host'),
        'NAME': os.environ.get('DB_NAME', 'database'),
        'PORT': os.environ.get('DB_PORT', 1234),
        'USER': os.environ.get('DB_USERNAME', 'user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'pass'),
        'OPTIONS': {
            'driver': os.environ.get('DB_DRIVER', 'ODBC Driver 17 for SQL Server'),
            'extra_params': os.environ.get('DB_EXTRA_PARAMS', ''),
        },
    }
}
DATABASE_ROUTERS = ['wamtram.routers.WamtramRouter']


# Internationalisation.
USE_I18N = False
USE_L10N = True
USE_TZ = True
TIME_ZONE = "Australia/Perth"
LANGUAGE_CODE = "en-us"
DATE_INPUT_FORMATS = (
    "%d/%m/%Y",
    "%d/%m/%y",
    "%d-%m-%Y",
    "%d-%m-%y",
    "%d %b %Y",
    "%d %b, %Y",
    "%d %B %Y",
    "%d %B, %Y",
)
DATETIME_INPUT_FORMATS = (
    "%d/%m/%Y %H:%M",
    "%d/%m/%y %H:%M",
    "%d-%m-%Y %H:%M",
    "%d-%m-%y %H:%M",
)
AWST = ZoneInfo(TIME_ZONE)
UTC = ZoneInfo("UTC")


# Email settings.
EMAIL_HOST = os.environ.get("EMAIL_HOST", "email.host")
EMAIL_PORT = os.environ.get("EMAIL_PORT", 25)
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@dbca.wa.gov.au")
SERVER_EMAIL = DEFAULT_FROM_EMAIL
EMAIL_SUBJECT_PREFIX = os.environ.get("EMAIL_SUBJECT_PREFIX", "[Turtles DB] ")
ADMIN_EMAILS = os.environ.get("ADMIN_EMAILS", "").split(",")
if not DEBUG:
    ADMINS =[("Admin",os.environ.get("ADMIN_EMAILS", ""))]


# Static files (CSS, JavaScript, Images)
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_URL = "/static/"
STATICFILES_DIRS = (os.path.join(BASE_DIR, "wastd", "static"),)
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
WHITENOISE_ROOT = STATIC_ROOT
WHITENOISE_MANIFEST_STRICT = False

# Media (user-uploaded files)
MEDIA_URL = "/media/"


# Logging settings - log to stdout
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "%(asctime)s %(levelname)-10s %(name)-10s %(message)s"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "stream": sys.stdout,
            "level": "WARNING",
        },
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
            "formatter": "verbose",
        },
        "turtles": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "stream": sys.stdout,
            "level": "INFO",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console","mail_admins"],
            "level": "ERROR",
        },
        "turtles": {
            "handlers": ["turtles"],
            "level": "INFO",
        },
    },
}


# django-crispy-forms config
# See: http://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs
CRISPY_TEMPLATE_PACK = "bootstrap4"


# Grappelli admin
GRAPPELLI_ADMIN_TITLE = "Turtles Database data curation portal"
GRAPPELLI_INDEX_DASHBOARD = "wastd.dashboard.AdminDashboard"

# ODK Central
ODK_API_URL = os.environ.get("ODK_API_URL", "url")
ODK_API_EMAIL = os.environ.get("ODK_API_EMAIL", "email")
ODK_API_PASSWORD = os.environ.get("ODK_API_PASSWORD", "pass")
ODK_API_PROJECTID = os.environ.get("ODK_API_PROJECTID", "-1")

# Leaflet map widgets
LEAFLET_CONFIG = {
    "SPATIAL_EXTENT": (-180, -90, 180, 90),
    "DEFAULT_CENTER": (-25, 120),
    "DEFAULT_ZOOM": 4,
    "MAX_ZOOM": 17,
    "SCALE": "metric",
    "MINIMAP": False,
    "PLUGINS": {
        "forms": {"auto-include": True},
        "markers": {"auto-include": True},
        "label": {"auto-include": True},
        "fullscreen": {"auto-include": True},
        "markercluster": {"auto-include": True},
        "tilelayer": {
            "auto-include": True
        },
    },
    "TILES": [
        (
            "Aerial Image",
            "//server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            {
                "attribution": "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community"
            },
        ),
        (
            "Place names",
            "http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
            {
                "attribution": '&copy; <a href="//www.openstreetmap.org/copyright">OpenStreetMap</a>'
            },
        ),
    ],
}

# Phone number
PHONENUMBER_DB_FORMAT = "INTERNATIONAL"

# django-bootstrap4 preconfigured settings.
# Reference: https://django-bootstrap4.readthedocs.io/en/latest/settings.html
BOOTSTRAP4 = {
    'success_css_class': '',  # Don't add `is-valid` to every form field by default.
}
