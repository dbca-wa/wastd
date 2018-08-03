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
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

d = os.path.abspath('.')
dot_env = os.path.join(str(d), '.env')
if os.path.exists(dot_env):
    confy.read_environment_file(dot_env)            # Must precede dj_static imports.
    #print("wsgi.py: .env found")
else:
    print("wsgi.py: .env missing at".format(dot_env))

from django.core.wsgi import get_wsgi_application   # noqa
from dj_static import Cling, MediaCling             # noqa

application = Cling(MediaCling(get_wsgi_application()))
