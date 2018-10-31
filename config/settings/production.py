# -*- coding: utf-8 -*-
"""
Production Configurations.

- Use djangosecure
- Use Amazon's S3 for storing static files and uploaded media
- Use mailgun to send emails
- Use Redis on Heroku


"""
from __future__ import absolute_import, unicode_literals

# import os
# from boto.s3.connection import OrdinaryCallingFormat, SubdomainCallingFormat
# from django.utils import six
from confy import env

from .common import *  # noqa

# SECRET CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Raises ImproperlyConfigured exception if DJANGO_SECRET_KEY not in os.environ
# unless default is set
SECRET_KEY = env('DJANGO_SECRET_KEY', default="CHANGEME")


# This ensures that Django will be able to detect a secure connection
# properly on Heroku.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# Use Whitenoise to serve static files
# See: https://whitenoise.readthedocs.io/
# WHITENOISE_MIDDLEWARE = ('whitenoise.middleware.WhiteNoiseMiddleware', )
# MIDDLEWARE_CLASSES = WHITENOISE_MIDDLEWARE + MIDDLEWARE_CLASSES
# STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# SECURITY CONFIGURATION
# ------------------------------------------------------------------------------
# See https://docs.djangoproject.com/en/1.9/ref/middleware/#module-django.middleware.security
# and https://docs.djangoproject.com/ja/1.9/howto/deployment/checklist/#run-manage-py-check-deploy
# Allow non-SSO logins using prod settings but local hosting (http) with DJANGO_SECURE=False
SECURE = env('DJANGO_SECURE', default=True)
if SECURE:
    # set this to 60 seconds and then to 518400 when you can prove it works
    SECURE_HSTS_SECONDS = 60
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env('DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True)
    SECURE_CONTENT_TYPE_NOSNIFF = env('DJANGO_SECURE_CONTENT_TYPE_NOSNIFF', default=True)
    SECURE_BROWSER_XSS_FILTER = env('DJANGO_SECURE_BROWSER_XSS_FILTER', default=True)
    SESSION_COOKIE_SECURE = env('DJANGO_SESSION_COOKIE_SECURE', default=True)
    SESSION_COOKIE_HTTPONLY = env('DJANGO_SESSION_COOKIE_HTTPONLY', default=True)
    SECURE_SSL_REDIRECT = env('DJANGO_SECURE_SSL_REDIRECT', default=False)
    CSRF_COOKIE_SECURE = env('DJANGO_CSRF_COOKIE_SECURE', default=True)
    CSRF_COOKIE_HTTPONLY = env('DJANGO_CSRF_COOKIE_HTTPONLY', default=True)
    X_FRAME_OPTIONS = env('DJANGO_X_FRAME_OPTIONS', default='DENY')

# Session management
# http://niwinz.github.io/django-redis/latest/#_configure_as_cache_backend
# SESSION_ENGINE = "django.contrib.sessions.backends.cache"  # use Redis
# SESSION_CACHE_ALIAS = "default"


# SITE CONFIGURATION
# ------------------------------------------------------------------------------
# Hosts/domain names that are valid for this site
# See https://docs.djangoproject.com/en/1.6/ref/settings/#allowed-hosts
# as per env variables
# END SITE CONFIGURATION


# STORAGE CONFIGURATION
# ------------------------------------------------------------------------------
# Uploaded Media Files
# ------------------------
# See: http://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html
# INSTALLED_APPS += ('storages', )
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
# AWS_CALLING_FORMAT = SubdomainCallingFormat
# AWS_ACCESS_KEY_ID = env('DJANGO_AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY = env('DJANGO_AWS_SECRET_ACCESS_KEY')
# AWS_STORAGE_BUCKET_NAME = env('DJANGO_AWS_STORAGE_BUCKET_NAME')
# # AWS_AUTO_CREATE_BUCKET = False
# # AWS_QUERYSTRING_AUTH = False
# AWS_EXPIRY = 60 * 60 * 24 * 7
# AWS_HEADERS = {'Cache-Control': six.b('max-age={0}, s-maxage={0}, must-revalidate'.format(AWS_EXPIRY))}
# STORAGE_BASE_URL = 'https://{0}.s3.amazonaws.com/'.format(AWS_STORAGE_BUCKET_NAME)

# MEDIA CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
# MEDIA_ROOT = str(APPS_DIR('media'))
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
# MEDIA_URL = '/media/'
# MEDIA_URL = STORAGE_BASE_URL + 'media/'


# Static Assets
# ------------------------
# MIDDLEWARE_CLASSES += ('whitenoise.middleware.WhiteNoiseMiddleware', )
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# STATIC_URL = STORAGE_BASE_URL + 'static/'
# STATICFILES_STORAGE = DEFAULT_FILE_STORAGE


# COMPRESSOR
# ------------------------------------------------------------------------------
# COMPRESS_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
# COMPRESS_URL = STATIC_URL
# COMPRESS_ENABLED = env('COMPRESS_ENABLED', default=True)

# TEMPLATE CONFIGURATION
# ------------------------------------------------------------------------------
# See:
# https://docs.djangoproject.com/en/dev/ref/templates/api/#django.template.loaders.cached.Loader
TEMPLATES[0]['OPTIONS']['loaders'] = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader', ]), ]


# CACHING
# ------------------------------------------------------------------------------
# Heroku URL does not pass the DB number, so we parse it in
# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': '{0}/{1}'.format(env('REDIS_URL', default='redis://127.0.0.1:6379'), 0),
#         'OPTIONS': {
#             'CLIENT_CLASS': 'django_redis.client.DefaultClient',
#             'IGNORE_EXCEPTIONS': True,  # mimics memcache behavior.
#                                         # http://niwinz.github.io/django-redis/latest/#_memcached_exceptions_behavior
#         }
#     }
# }


# Custom Admin URL, use {% url 'admin:index' %}
# ADMIN_URL = env('DJANGO_ADMIN_URL')

# Your production stuff: Below this line define 3rd party library settings
