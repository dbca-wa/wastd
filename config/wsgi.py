"""
WSGI config for WAStD project.

This module contains the WSGI application used by Django's development server
and any production WSGI deployments. It should expose a module-level variable
named ``application``. Django's ``runserver`` and ``runfcgi`` commands discover
this application via the ``WSGI_APPLICATION`` setting.

Usually you will have the standard Django WSGI application here, but it also
might make sense to replace the whole Django WSGI application with a custom one
that later delegates to the Django one. For example, you could introduce WSGI
middleware here, or combine a Django application with an application of another
framework.

"""
import confy
import os
from dj_static import Cling, MediaCling
from django.core.wsgi import get_wsgi_application
# from whitenoise import WhiteNoise
# from config.settings.production import STATIC_ROOT

confy.read_environment_file()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")
# application = WhiteNoise(get_wsgi_application(), root=STATIC_ROOT)
# application.add_files('/path/to/more/static/files', prefix='more-files/')


application = Cling(MediaCling(get_wsgi_application()))

# Apply WSGI middleware here.
# from helloworld.wsgi import HelloWorldApplication
# application = HelloWorldApplication(application)
