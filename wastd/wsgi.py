"""
WSGI config for WAStD project.
It exposes the WSGI callable as a module-level variable named ``application``.
"""
from django.core.wsgi import get_wsgi_application
import os
from pathlib import Path

# These lines are required for interoperability between local and container environments.
d = Path(__file__).resolve().parents[1]
dot_env = os.path.join(str(d), '.env')
if os.path.exists(dot_env):
    from dotenv import load_dotenv
    load_dotenv()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wastd.settings')
application = get_wsgi_application()
