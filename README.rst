WAStD
==============================
WA Sea Turtle and Strandings Database

* WA Strandings Database: Marine Wildlife Incidents managed by DBCA
* WA Sea Turtle Database: Sea turtle tagging and nesting census

.. image:: https://github.com/dbca-wa/wastd/workflows/CodeQL/badge.svg?branch=master
     :target: https://github.com/dbca-wa/wastd/actions
     :alt: CodeQL
.. image:: https://github.com/dbca-wa/wastd/workflows/DjangoCI/badge.svg?branch=master
     :target: https://github.com/dbca-wa/wastd/actions
     :alt: DjangoCI
.. image:: https://coveralls.io/repos/github/dbca-wa/wastd/badge.svg?branch=master
     :target: https://coveralls.io/github/dbca-wa/wastd?branch=master
     :alt: Test coverage
.. image:: https://img.shields.io/badge/License-MIT-green.svg
     :target: https://opensource.org/licenses/MIT
     :alt: MIT License


How to use: Read the `docs <https://dbca-wa.github.io/wastd/index.html>`_.


Admin
-----

Setting Up Your Users
^^^^^^^^^^^^^^^^^^^^^

* To create a **normal user account**, just go to Sign Up and fill out the form.
  Once you submit it, you'll see a "Verify Your E-mail Address" page.
  Go to your console to see a simulated email verification message.
  Copy the link into your browser. Now the user's email should be verified and ready to go.

* To create an **superuser account**, use this command::

    $ python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your
superuser logged in on Firefox (or similar), so that you can see how the site
behaves for both kinds of users.


Maintenance
-----------
RKS instructions


Development
-----------

Set up dev
^^^^^^^^^^
TODO update instructions.

First, create a postgis database on an available database cluster.::

    export CLUSTERNAME=sdis
    export CLUSTERPORT=5444
    export PG_VERSION=10
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
