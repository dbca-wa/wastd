
Migration to Kubernetes
=======================

* Spin up a VM and install [Rancher](https://rancher.com/products/rancher/).
* Create a cluster, e.g. ``az-docker``.
* Create a project, e.g. ``eco`` with RAM limits.
* Create a namespace, e.g. ``tsc`` with memory limit 4092 MiB, container default mem limt 1024 MiB (these values might be too high).
* In namespace tsc, we will create workloads for db (housing PROD and UAT) and app (PROD and UAT separately).

Workload db
-----------
* Image ``mdillon/postgis:11``.
* Volumes: add new persistent storage claim (20 GiB), mount point ``/var/lib/postgresql/data``.
* Deploy, open shell in running container and execute:

  ::
  apt update && apt install -y openssh-client rsync
  rsync USER@HOST:/path/to/wastd.dump /tmp/
  psql -h localhost -U postgres

  # in psql shell
  create role wastd superuser login;
  alter role wastd password "SOME_PASSWORD";
  create database wastd_prod with owner wastd;
  create database wastd_uat with owner wastd;
  \q

  pg_restore -h localhost -U wastd -d wastd_prod < /tmp/wastd.dump
  pg_restore -h localhost -U wastd -d wastd_uat < /tmp/wastd.dump


Workloads prod/uat
------------------
* Images dbcawa/wastd:0.25.0 (or highest named tag for prod) dbcawa/wastd:latest (latest for uat)
* Env vars::

  DATABASE_URL="postgis://wastd:PASSWORD@db/wastd_prod" # or wastd_uat
  SITE_URL="https://tsc.dbca.wa.gov.au" # or tsc-uat
  SECRET_KEY=...
  PYPANDOC_PANDOC=/usr/bin/pandoc
  ODKA_URL="https://dpaw-data.appspot.com"
  ODKA_UN="USERNAME"
  ODKA_PW="PASSWORD"

* Port mapping: 8080 to random > start, let rancher choose free port > set chosen port permanently
* Health check: both readiness and liveness check: ``HTTP request returns a successful status (2xx or 3xx)``
* Scaling policy: ``start new, then stop old``
* Volumes: media-prod and media-uat, persistent storage claim, 500 GiB, mount point ``/usr/src/app/media``

Once workloads are running, copy media files into the storage volume from the app container's shell:

  ::
  root@prod-SOMEHASH:/usr/src/app# rsync -Pavvr USER@aws-eco-001.lan.fyi:/home/CORPORATEICT/USER/tsc/media/ media/

Local development environment
=============================

This section describes deployment in development (local) and production
environments (UAT, PROD).

Virtualenv
----------
Install virtualenv::

    sudo pip3 install virtualenvwrapper

Set virtualenv paths by adding these lines to your ~/.bashrc::

    export WORKON_HOME=/path/to/virtualenvs     # e.g. /home/USERNAME/.venvs
    export PROJECT_HOME=/path/to/projects       # e.g. /var/www/
    source /usr/local/bin/virtualenvwrapper.sh
    export PIP_VIRTUALENV_BASE=WORKON_HOME

Activate the virtualenv::

    mkproject -p /usr/bin/python3 wastd


vim ~/.venv/wastd/.project
/home/florian/projects/wastd



Database
--------
Create a PostgreSQL database with PostGIS, psql into an existing database
on an existing cluster::

    some_db=# create database wastd_8220 owner DBUSER;
    some_db=# \c wastd_8220 ;
    wastd_8220=# create extension postgis;
    wastd_8220=# \q

The database connection string will be in the format::

    DATABASE_URL="postgis://DBUSER:DBPASS@DBHOST:DBPORT/DBNAME"


Code
----
Install dependencies::

    workon wastd
    git clone git@github.com:dbca-wa/wastd.git .
    pip install Fabric3 django-confy
    fab pip
    cp env.example .env

Edit ``.env`` and enter your settings, particularly the database URL

Permissions
-----------
* Your local user shall be part of group www-data.
* Code and virtualenv shall be chowned by www-data:www-data with permissions
  775 (folders) and 664 (files).
* The production web server shall run under the www-data account.

Create folders, set permissions (files 0664, folders 0775)::

    mkdir staticfiles
    sudo chown -R www-data:www-data .
    find . -type f -exec sudo chmod 0664 {} \;
    find . -type d -exec sudo chmod 0775 {} \;
    sudo chmod +x manage.py

Same for virtualenv (paths depend on your virtualenv in .bashrc)::

    sudo chown -R YOUR_USER:www-data $WORKON_HOME/wastd/
    find $WORKON_HOME/wastd/ -type f -exec sudo chmod 0664 {} \;
    find $WORKON_HOME/wastd/ -type d -exec sudo chmod 0775 {} \;
    sudo chmod -R +x $WORKON_HOME/wastd/bin/*

Setup the database::

    ./manage.py migrate

Sync data and files::

    (wastd)me@UAT:~/projects/wastd$ rsync -Pavvr wastd/media/ me@PROD:/mnt/projects/wastd/wastd/media/
    (wastd)me@UAT:~/projects/wastd$ ./manage.py dumpdata --natural-primary --natural-foreign --indent 4 > data.json
    (wastd)me@UAT:~/projects/wastd$ rsync -Pavvr data.json me@PROD:/mnt/projects/wastd/
    (wastd)me@PROD:/mnt/projects/wastd$ ./manage.py loaddata data.json

Run ``fab static`` and ``fab go`` to see WAStD running in dev.


Getting data from PROD via gateway server to DEV::

    (wastd)florianm@aws-eco-001:/mnt/projects/wastd$ ./manage.py dumpdata --natural-primary --natural-foreign --indent 4 > data.json
    (wastd)florianm@aws-eco-001:/mnt/projects/wastd$ pg_dump -h localhost -p DBPORT -U DBUSER -Fc wastd_8220 > wastd_8220.dump
    (wastd)florianm@aws-eco-001:/mnt/projects/wastd$ rsync -Pavvr data.json florianm@kens-xenmate-dev:/home/CORPORATEICT/florianm
    (wastd)florianm@aws-eco-001:/mnt/projects/wastd$ rsync -Pavvr wastd_8220.dump florianm@kens-xenmate-dev:/home/CORPORATEICT/florianm
    (wastd)florianm@aws-eco-001:/mnt/projects/wastd$ rsync -Pavvr wastd/media/ florianm@kens-xenmate-dev:/home/CORPORATEICT/florianm/wastd/wastd/media/


    (wastd) florianm@kens-awesome-001:~/projects/dpaw/wastd⟫ rsync -Pavvr florianm@kens-xenmate-dev:/home/CORPORATEICT/florianm/data.json data
    (wastd) florianm@kens-awesome-001:~/projects/dpaw/wastd⟫ rsync -Pavvr florianm@kens-xenmate-dev:/home/CORPORATEICT/florianm/wastd_8220.dump data
    (wastd) florianm@kens-awesome-001:~/projects/dpaw/wastd⟫ rsync -Pavvr florianm@kens-xenmate-dev:/home/CORPORATEICT/florianm/wastd/wastd/media/ wastd/media/
    (wastd) florianm@kens-awesome-001:~/projects/dpaw/wastd⟫ ./manage.py loaddata data/data.json
    # or:
    (wastd) florianm@kens-awesome-001:~/projects/dpaw/wastd⟫ pg_restore -h localhost -p DBPORT -U DBUSER -d wastd_8220 < data/wastd_8220.dump


Useful commands
---------------

* ``fab go``: run development server with local settings on .env's PORT
* ``fab pro``: run development server with production settings on .env's PORT
* ``fab shell``: run shell_plus
* ``fab static``: delete, then collect (link) staticfiles
* ``fab -l``: see all available commands

Production server 1: Supervisord
--------------------------------
Install supervisor with ``sudo apt-get install supervisor``.
Create `/etc/supervisor/conf.d/wastd.conf`::

    [program:wastd]
    user=APPUSER
    stopasgroup=true
    autostart=true
    autorestart=true
    directory=/path/to/code/wastd
    command=/path/to/.virtualenvs/wastd/bin/honcho run gunicorn config.wsgi
    environment=PATH="/path/to/.virtualenvs/wastd/bin/:%(ENV_PATH)s",PYTHONUNBUFFERED="true"

Run the app::

    ./manage.py collectstatic --noinput
    sudo supervisorctl restart wastd

Production server 2: uwsgi
--------------------------
Install uwsgi system-wide::

    sudo pip install uwsgi

Create folders and set ownership::

    (wastd)me@PROD:/mnt/projects/wastd$ sudo mkdir -p /var/spool/uwsgi/spooler
    (wastd)me@PROD:/mnt/projects/wastd$ sudo mkdir -p /var/spool/uwsgi/sockets
    (wastd)me@PROD:/mnt/projects/wastd$ sudo mkdir -p /var/log/uwsgi/
    (wastd)me@PROD:/mnt/projects/wastd$ sudo touch /var/log/uwsgi/emperor.log
    (wastd)me@PROD:/mnt/projects/wastd$ sudo chown -R www-data:www-data /var/spool/uwsgi/
    (wastd)me@PROD:/mnt/projects/wastd$ sudo chown -R www-data:www-data /var/log/uwsgi/
    (wastd)me@PROD:/mnt/projects/wastd$ sudo mkdir -p /etc/uwsgi/vassals/
    (wastd)me@PROD:/mnt/projects/wastd$ cp config/wastd_uwsgi.ini.template config/wastd_uwsgi.ini
    (wastd)me@PROD:/mnt/projects/wastd$ vim config/wastd_uwsgi.ini # set your paths
    (wastd)me@PROD:/mnt/projects/wastd$ ln -s config/wastd_uwsgi.ini /etc/uwsgi/vassals/wastd_uwsgi.ini

Create a file /etc/init/uwsgi.conf with these contents::

    # Emperor uWSGI script

    description "uWSGI Emperor"
    start on runlevel [2345]
    stop on runlevel [06]

    respawn

    exec /usr/local/bin/uwsgi --vassals-include-before /etc/uwsgi/defaults.ini --emperor "/etc/uwsgi/vassals/*.ini" --emperor-stats /var/spool/uwsgi/sockets/stats_emperor.sock --logto /var/log/uwsgi/emperor.log --spooler "/var/spool/uwsgi/spooler" --uid www-data --gid www-data

Create a file ``/etc/uwsgi/defaults.ini``::

    [uwsgi]
    # sensible defaults for an uWSGI application, can be overridden in the local config file
    processes       = 4
    gevent          = 100
    gevent-early-monkey-patch = true
    max-requests    = 1000
    buffer-size     = 32768
    cache2          = name=default,bitmap=1,items=10000,blocksize=1000,blocks=200000
    vacuum          = true
    memory-report   = true
    auto-procname   = true
    logdate         = %%Y/%%m/%%d %%H:%%M:%%S

Then start the uwsgi service with ``sudo service uwsgi start``.

Deploying upgrades to production
================================
To roll out upgrades to a production server, these steps should work in most
cases::

    ssh production-server-name
    workon wastd
    git pull
    fab deploy

    # if running with supervisord:
    sudo supervisorctl restart wastd

    # if running with uwsgi:
    sudo service uwsgi restart

Developing with Docker
======================

You can develop your application in a `Docker`_ container for simpler
deployment onto bare Linux machines later. This instruction assumes an
`Amazon Web Services`_ EC2 instance, but it should work on any machine with
Docker > 1.3 and `Docker compose`_ installed.

.. _Docker: https://www.docker.com/
.. _Amazon Web Services: http://aws.amazon.com/
.. _Docker compose: https://docs.docker.com/compose/

Setting up
----------

Docker encourages running one container for each process. This might mean one
container for your web server, one for Django application and a third for your
database. Once you're happy composing containers in this way you can easily
add more, such as a `Redis`_ cache.

.. _Redis: http://redis.io/

The Docker compose tool (previously known as `fig`_) makes linking these
containers easy. An example set up for your Cookiecutter Django project might
look like this:

.. _fig: http://www.fig.sh/

::

    webapp/ # Your cookiecutter project would be in here
        Dockerfile
        ...
    database/
        Dockerfile
        ...
    webserver/
        Dockerfile
        ...
    docker-compose.yml

Each component of your application would get its own `Dockerfile`_.
The rest of this example assumes you are using the `base postgres image`_ for
your database. Your database settings in `config/common.py` might then look
something like:

.. _Dockerfile: https://docs.docker.com/reference/builder/
.. _base postgres image: https://registry.hub.docker.com/_/postgres/

.. code-block:: python

    DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': 'postgres',
                'USER': 'postgres',
                'HOST': 'database',
                'PORT': 5432,
            }
        }

The `Docker compose documentation`_ explains in detail what you can accomplish
in the `docker-compose.yml` file, but an example configuration might look like this:

.. _Docker compose documentation: https://docs.docker.com/compose/#compose-documentation

.. code-block:: yaml

    database:
        build: database
    webapp:
        build: webapp:
        command: /usr/bin/python3.4 manage.py runserver 0.0.0.0:8000 # dev setting
        # command: gunicorn -b 0.0.0.0:8000 wsgi:application # production setting
        volumes:
            - webapp/your_project_name:/path/to/container/workdir/
        links:
            - database
    webserver:
        build: webserver
        ports:
            - "80:80"
            - "443:443"
        links:
            - webapp

We'll ignore the webserver for now (you'll want to comment that part out while we do).
A working Dockerfile to run your cookiecutter application might look like this::

    FROM ubuntu:14.04
    ENV REFRESHED_AT 2015-01-13

    # update packages and prepare to build software
    RUN ["apt-get", "update"]
    RUN ["apt-get", "-y", "install", "build-essential", "vim", "git", "curl"]
    RUN ["locale-gen", "en_GB.UTF-8"]

    # install latest python
    RUN ["apt-get", "-y", "build-dep", "python3-dev", "python3-imaging"]
    RUN ["apt-get", "-y", "install", "python3-dev", "python3-imaging", "python3-pip"]

    # prepare postgreSQL support
    RUN ["apt-get", "-y", "build-dep", "python3-psycopg2"]

    # move into our working directory
    # ADD must be after chown see http://stackoverflow.com/a/26145444/1281947
    RUN ["groupadd", "python"]
    RUN ["useradd", "python", "-s", "/bin/bash", "-m", "-g", "python", "-G", "python"]
    ENV HOME /home/python
    WORKDIR /home/python
    RUN ["chown", "-R", "python:python", "/home/python"]
    ADD ./ /home/python

    # manage requirements
    ENV REQUIREMENTS_REFRESHED_AT 2015-02-25
    RUN ["pip3", "install", "-r", "requirements.txt"]

    # uncomment the line below to use container as a non-root user
    USER python:python

Running `sudo docker-compose build` will follow the instructions in your
`docker-compose.yml` file and build the database container, then your webapp,
before mounting your cookiecutter project files as a volume in the webapp
container and linking to the database. Our example yaml file runs in development
mode but changing it to production mode is as simple as commenting out the line
using `runserver` and uncommenting the line using `gunicorn`.

Both are set to run on port `0.0.0.0:8000`, which is where the Docker daemon
will discover it. You can now run `sudo docker-compose up` and browse to
`localhost:8000` to see your application running.

Deployment
----------

You'll need a webserver container for deployment. An example setup for `Nginx`_

might look like this::

    FROM ubuntu:14.04
    ENV REFRESHED_AT 2015-02-11

    # get the nginx package and set it up
    RUN ["apt-get", "update"]
    RUN ["apt-get", "-y", "install", "nginx"]

    # forward request and error logs to docker log collector
    RUN ln -sf /dev/stdout /var/log/nginx/access.log
    RUN ln -sf /dev/stderr /var/log/nginx/error.log
    VOLUME ["/var/cache/nginx"]
    EXPOSE 80 443

    # load nginx conf
    ADD ./site.conf /etc/nginx/sites-available/your_cookiecutter_project
    RUN ["ln", "-s", "/etc/nginx/sites-available/your_cookiecutter_project", "/etc/nginx/sites-enabled/your_cookiecutter_project"]
    RUN ["rm", "-rf", "/etc/nginx/sites-available/default"]

    #start the server
    CMD ["nginx", "-g", "daemon off;"]

.. _Nginx: http://wiki.nginx.org/Main

That Dockerfile assumes you have an Nginx conf file named `site.conf` in the same
directory as the webserver Dockerfile. A very basic example, which forwards
traffic onto the development server or gunicorn for processing, would look like this::

    # see http://serverfault.com/questions/577370/how-can-i-use-environment-variables-in-nginx-conf#comment730384_577370
    upstream localhost {
        server webapp_1:8000;
    }
    server {
        location / {
            proxy_pass http://localhost;
        }
    }

Running `sudo docker-compose build webserver` will build your server container.
Running `sudo docker-compose up` will now expose your application directly on
`localhost` (no need to specify the port number).

Building and running your app on EC2
-------------------------------------

All you now need to do to run your app in production is:

* Create an empty EC2 Linux instance (any Linux machine should do).

* Install your preferred source control solution, Docker and Docker compose on
  the news instance.

* Pull in your code from source control. The root directory should be the one
  with your `docker-compose.yml` file in it.

* Run `sudo docker-compose build` and `sudo docker-compose up`.

* Assign an `Elastic IP address`_ to your new machine.

.. _Elastic IP address: https://aws.amazon.com/articles/1346

* Point your domain name to the elastic IP.

**Be careful with Elastic IPs** because, on the AWS free tier, if you assign
one and then stop the machine you will incur charges while the machine is down
(presumably because you're preventing them allocating the IP to someone else).

Security advisory
-----------------

The setup described in this instruction will get you up-and-running but it
hasn't been audited for security. If you are running your own setup like this
it is always advisable to, at a minimum, examine your application with a tool
like `OWASP ZAP`_ to see what security holes you might be leaving open.

.. _OWASP ZAP: https://www.owasp.org/index.php/OWASP_Zed_Attack_Proxy_Project
