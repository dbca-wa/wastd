import os
import sys
import tomllib
from pathlib import Path
from zoneinfo import ZoneInfo

import dj_database_url
from dbca_utils.utils import env
from django.core.exceptions import DisallowedHost
from django.db.utils import OperationalError

# Build paths inside the project like this: os.path.join(BASE_DIR, "subdir")
BASE_DIR = Path(__file__).resolve().parent.parent


# Settings defined in environment variables.
DEBUG = env("DEBUG", False)
SECRET_KEY = env("SECRET_KEY", "PlaceholderSecretKey")
CSRF_COOKIE_SECURE = env("CSRF_COOKIE_SECURE", False)
CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS", "http://127.0.0.1").split(",")
SESSION_COOKIE_SECURE = env("SESSION_COOKIE_SECURE", False)
SECURE_SSL_REDIRECT = env("SECURE_SSL_REDIRECT", False)
SECURE_REFERRER_POLICY = env("SECURE_REFERRER_POLICY", None)
SECURE_HSTS_SECONDS = env("SECURE_HSTS_SECONDS", 0)
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

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        # Use whitenoise to add compression and caching support for static files.
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Assume Azure blob storage is used for media uploads, unless explicitly set as local storage.
LOCAL_MEDIA_STORAGE = env("LOCAL_MEDIA_STORAGE", False)
if LOCAL_MEDIA_STORAGE:
    MEDIA_ROOT = os.path.join(BASE_DIR, "media")
    # Ensure that the local media directory exists.
    if not os.path.exists(MEDIA_ROOT):
        os.makedirs(MEDIA_ROOT)
else:
    STORAGES["default"] = {
        "BACKEND": "storages.backends.azure_storage.AzureStorage",
    }
    AZURE_ACCOUNT_NAME = env("AZURE_ACCOUNT_NAME", "name")
    AZURE_ACCOUNT_KEY = env("AZURE_ACCOUNT_KEY", "key")
    AZURE_CONTAINER = env("AZURE_CONTAINER", "container")
    AZURE_URL_EXPIRATION_SECS = env("AZURE_URL_EXPIRATION_SECS", 3600)  # Default one hour.

# Application settings
INSTALLED_APPS = [
    "whitenoise.runserver_nostatic",
    "polymorphic",  # Before django.contrib.contenttypes
    "django.contrib.contenttypes",
    "grappelli.dashboard",
    "grappelli",  # Before django.contrib.admin
    "django.contrib.admin",
    "nested_admin",
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
    "mapwidgets",
    "phonenumber_field",
    "crispy_forms",
    "bootstrap4",
    "webtemplate_dbca",
    "django_filters",
    "export_download",
    "django_tables2",
    "django_select2",
    "easy_select2",
    "djgeojson",
    "import_export",
    # Local apps
    "users",
    "observations",
    "marine_mammal_incidents",
    "wamtram2"
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

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "wastd", "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "debug": DEBUG,
            "libraries": {
                "proper_paginate": "wastd.templatetags.proper_paginate",
                "url_replace": "wastd.templatetags.url_replace",
                "dict_filter": "wastd.templatetags.dict_filter",
            },
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
            "style": "mapbox://styles/dpawasi/ckigwmxrx606g19msw0g882gj",
            #"style": "mapbox://styles/mapbox/streets-v11",
        },
        "geocoderOptions": {
            "zoom": 7,
            "countries": "au"
        }
    }
}
GEOSERVER_URL = os.environ.get("GEOSERVER_URL", "")
IMPORT_EXPORT_SKIP_ADMIN_CONFIRM = True

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
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"

# Branding
SITE_NAME = os.environ.get("SITE_NAME", "Turtles Database")
SITE_TITLE = os.environ.get("SITE_TITLE", "Turtles Database")
SITE_CODE = os.environ.get("SITE_CODE", "Turtles")
project = tomllib.load(open(os.path.join(BASE_DIR, "pyproject.toml"), "rb"))
VERSION_NO = project["tool"]["poetry"]["version"]


# Database configuration
DATABASES = {
    # Defined in DATABASE_URL env variable.
    'default': dj_database_url.config(default=os.getenv('DATABASE_URL')),
    "wamtram2": {
        "ENGINE": "mssql",
        "HOST": os.environ.get("DB_HOST", "host"),
        "NAME": os.environ.get("DB_NAME", "database"),
        "PORT": os.environ.get("DB_PORT", 1234),
        "USER": os.environ.get("DB_USERNAME", "user"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "user"),
        "OPTIONS": {
            "driver": os.environ.get("DB_DRIVER", "ODBC Driver 18 for SQL Server"),
            "extra_params": os.environ.get("DB_EXTRA_PARAMS", ""),
        },
    },
}
DATABASE_ROUTERS = ["wamtram2.routers.Wamtram2Router"]


# Internationalisation.
USE_I18N = False
USE_TZ = True
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
TIME_ZONE = "Australia/Perth"
TZ = ZoneInfo(TIME_ZONE)
UTC = ZoneInfo("UTC")
# USE_TZ = False


# Email settings.
EMAIL_HOST = os.environ.get("EMAIL_HOST", "email.host")
EMAIL_PORT = os.environ.get("EMAIL_PORT", 25)
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@dbca.wa.gov.au")
SERVER_EMAIL = DEFAULT_FROM_EMAIL
EMAIL_SUBJECT_PREFIX = os.environ.get("EMAIL_SUBJECT_PREFIX", "[Turtles DB] ")
ADMIN_EMAILS = os.environ.get("ADMIN_EMAILS", "").split(",")


# Static files (CSS, JavaScript, Images)
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_URL = "/static/"
STATICFILES_DIRS = (os.path.join(BASE_DIR, "wastd", "static"),)
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
            "handlers": ["console", "mail_admins"],
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


# Phone number
PHONENUMBER_DB_FORMAT = "INTERNATIONAL"

# django-bootstrap4 preconfigured settings.
# Reference: https://django-bootstrap4.readthedocs.io/en/latest/settings.html
BOOTSTRAP4 = {
    'success_css_class': '',  # Don't add `is-valid` to every form field by default.
}


def sentry_excluded_exceptions(event, hint):
    """Exclude defined class(es) of Exception from being reported to Sentry.
    These exception classes are generally related to operational or configuration issues,
    and they are not errors that we want to capture.
    https://docs.sentry.io/platforms/python/configuration/filtering/#filtering-error-events
    """
    if "exc_info" in hint and hint["exc_info"]:
        # Exclude database-related errors (connection error, timeout, DNS failure, etc.)
        if hint["exc_info"][0] is OperationalError:
            return None
        # Exclude exceptions related to host requests not in ALLOWED_HOSTS.
        elif hint["exc_info"][0] is DisallowedHost:
            return None

    return event


# Sentry config
SENTRY_DSN = env("SENTRY_DSN", None)
SENTRY_SAMPLE_RATE = env("SENTRY_SAMPLE_RATE", 1.0)  # Error sampling rate
SENTRY_TRANSACTION_SAMPLE_RATE = env("SENTRY_TRANSACTION_SAMPLE_RATE", 0.0)  # Transaction sampling
SENTRY_PROFILES_SAMPLE_RATE = env("SENTRY_PROFILES_SAMPLE_RATE", 0.0)  # Proportion of sampled transactions to profile.
SENTRY_ENVIRONMENT = env("SENTRY_ENVIRONMENT", None)
if SENTRY_DSN and SENTRY_ENVIRONMENT:
    import sentry_sdk

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        sample_rate=SENTRY_SAMPLE_RATE,
        traces_sample_rate=SENTRY_TRANSACTION_SAMPLE_RATE,
        profiles_sample_rate=SENTRY_PROFILES_SAMPLE_RATE,
        environment=SENTRY_ENVIRONMENT,
        release=VERSION_NO,
        before_send=sentry_excluded_exceptions,
    )
