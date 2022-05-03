.. _app-maintainers:
***********************
Application maintainers
***********************

Set up development environment
==============================

* Install pyenv.
* Install shell completions, e.g. fish: https://gist.github.com/sirkonst/e39bc28218b57cc78b6f728b8da99f33
* Good pyenv intro: https://realpython.com/intro-to-pyenv/
* Use pyenv to install Python 3.10.4 or later.
* Clone WAStD repo.
* Use pyenv to create a virtualenv followign `<https://realpython.com/intro-to-pyenv/>`_
* ``pyenv virtualenv 3.10.4 wastd`` 
  with ``3.10.4`` being the latest Python version available at the time of writing.
* ``pyenv local wastd``
* Install dependencies through ``poetry install --no-root``.

Alternatives: Develop with Docker / docker-compose following https://docs.docker.com/samples/django/.

Day to day development
======================

* Enter WAStD repo, which activates the virtualenv.
* TODO this does not load vars from ``.env`` yet.
* Ballmer.jpg
* Run tests with ``fab test``.
* Deactivate virtualenv with ``source deavtivate``.

Add a new dependency:
* ``poetry add <package>``
* ``poetry run pip list --format=freeze > requirements/base.txt``

Release
=======

Pre-release
-----------

* Write tests.
* Write docs (user manual).
* Commit changes.
* Build Dockerfile locally and test changes: 

  * ``docker build -t dbcawa/wastd:latest .`` or ``fab dbuild``
  * ``docker run -it dbcawa/wastd:latest``
* Portainer is a great UI to run and inspect local Docker images.

Release
-------

* Edit ``.env`` with new ``WASTD_RELEASE``.
* Deactivate virtualenv with ``source deavtivate``.
* Activate virtualenv with ``poetry env use 3.10.4`` to read new ``WASTD_RELEASE``
* Run ``fab tag`` to create a new git tag, push commits, then push the tag. 
* GH Actions will build and publish the Docker image to ghcr.io.

Deploy
------

* Open Rancher UI and edit the UAT config for WAStD workload to the new version number. 
  This will download the Docker image (which can take a few mins), then hot-swap the images.
* Apply migrations if any through a shell on the respective workload with ``./manage.py migrate``.
* Once running and tested, edit PROD. 
  Since the Docker image is already downloaded, this step will be fast. 
  Run db migrations if necessary.


Useful commands
===============
Create a postgis database on an available database cluster.::

    export CLUSTERNAME=sdis
    export CLUSTERPORT=5444
    export PG_VERSION=14
    sudo -u postgres pg_createcluster -p $CLUSTERPORT $PG_VERSION $CLUSTERNAME --start && \
    sudo -u postgres createuser -s $CLUSTERNAME -p $CLUSTERPORT -P && \
    sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" /etc/postgresql/$PG_VERSION/$CLUSTERNAME/postgresql.conf && \
    sed -i "s/#wal_level = minimal/wal_level = archive/" /etc/postgresql/$PG_VERSION/$CLUSTERNAME/postgresql.conf && \
    sed -i "s/127.0.0.1\/32/10.0.0.0\/8/" /etc/postgresql/$PG_VERSION/$CLUSTERNAME/pg_hba.conf && \
    sudo systemctl restart postgresql@$PG_VERSION-$CLUSTERNAME restart

Create a virtualenv project, clone this repo and pip install the requirements::

    $ mkproject wastd
    (wastd) path/to/wastd:$ git clone git@github.com:dbca-wa/wastd.git
    $ pip install -r requirements/dev.txt
    $ cp env.example .env

.env must contain a working DATABASE_URL, such as (with your respective DBUSER,
DBPASS, HOST, PORT)::

    DATABASE_URL="postgis://DBUSER:DBPASS@HOST:PORT/DBNAME"

See env.example for other useful settings.

Then, migrate the database and start the app::

    $ fab migrate
    $ fab go


Permissions
^^^^^^^^^^^
Source: `SO <https://stackoverflow.com/a/805453/2813717>`_.
See also `this post <https://stackoverflow.com/a/16409205/2813717>`_.


Chown the entire project to the webserver's user and group and
set permissions to 775 for directories, 664 for files::

    sudo chown -R www-data:www-data .
    find . -type d -exec sudo chmod 775 {} \;
    find . -type f -exec sudo chmod 664 {} \;

This lets the server admin run commands and edit files
as long as the admin is in the same group as the webserver, e.g. www-data.


Data migration
^^^^^^^^^^^^^^
Restoring a snapshot of the production database to a development environment::

    (wastd)florianm@aws-eco-001:~/projects/wastd$ pg_dump -h localhost -p 5443 -U sdis -Fc wastd_8220 > data/wastd.dump
    (wastd)florianm@aws-eco-001:~/projects/wastd$ rsync -Pavvr data/wastd.dump kens-xenmate-dev:/home/CORPORATEICT/florianm
    (wastd)florianm@aws-eco-001:~/projects/wastd$ rsync -Pavvr wastd/media kens-xenmate-dev:/home/CORPORATEICT/florianm/wastd/media

    # LOCAL
    ./manage.py dbshell
    # drop database wastd; create database wastd owner sdis; \q
    (wastd)florianm@kens-awesome-001:~/projects/wastd⟫ rsync -Pavvr kens-xenmate-dev:/home/CORPORATEICT/florianm/wastd.dump data/
    (wastd)florianm@kens-awesome-001:~/projects/wastd⟫ pg_restore -h localhost -p 5444 -U sdis -d wastd < data/wastd.dump
    (wastd)florianm@kens-awesome-001:~/projects/wastd⟫ rsync -Pavvr kens-xenmate-dev:/home/CORPORATEICT/florianm/wastd/media wastd/media

Double check file permissions after transfer.
