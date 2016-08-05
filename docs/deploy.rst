Deploy
========

This is where you describe how the project is deployed in production.

Create `/etc/supervisor/conf.d/wastd.conf`::

    [program:wastd]
    user=APPUSER
    stopasgroup=true
    autostart=true
    autorestart=true
    directory=/path/to/code/wastd
    command=/path/to/.virtualenvs/wastd/bin/honcho run gunicorn config.wsgi
    environment=PATH="/path/to/.virtualenvs/wastd/bin/:%(ENV_PATH)s",PYTHONUNBUFFERED="true"
