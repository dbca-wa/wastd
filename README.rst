WAStD
==============================

WA Stranding Database

.. image:: https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg
     :target: https://github.com/pydanny/cookiecutter-django/
     :alt: Built with Cookiecutter Django
.. image:: https://circleci.com/gh/florianm/wastd.svg?style=svg
     :target: https://circleci.com/gh/florianm/wastd
     :alt: Test status
.. image:: https://coveralls.io/repos/github/florianm/wastd/badge.svg?branch=master
     :target: https://coveralls.io/github/florianm/wastd?branch=master
     :alt: Test coverage

Note: A bug in the version of functools used by the continuous integration provider
currenntly lets all automated remote tests fail. Local testing passes however.

LICENSE: MIT

Setup the app
-------------
Create a virtualenv project, clone this repo and pip install the requirements::
    $ mkproject wastd
    (wastd) path/to/wastd:$ git clone git@github.com:florianm/wastd.git
    $ pip install -r requirements/production.txt
    $ pip install -r requirements/local.txt
    $ pip install -r requirements/test.txt
    $ touch .env

.env must contain a working DATABASE_URL, such as (with your respective DBUSER,
DBPASS, HOST, PORT)::
    DATABASE_URL="postgis://DBUSER:DBPASS@HOST:PORT/DBNAME"
See env.example for other useful settings.


Settings
------------

Moved to settings_.

.. _settings: http://cookiecutter-django.readthedocs.io/en/latest/settings.html

Basic Commands
--------------

Setting Up Your Users
^^^^^^^^^^^^^^^^^^^^^

* To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

* To create an **superuser account**, use this command::

    $ python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

Test coverage
^^^^^^^^^^^^^

To run the tests, check your test coverage, and generate an HTML coverage report::

    $ coverage run manage.py test
    $ coverage html
    $ open htmlcov/index.html

Running tests with py.test
~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ py.test


Live reloading and Sass CSS compilation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Moved to `Live reloading and SASS compilation`_.

.. _`Live reloading and SASS compilation`: http://cookiecutter-django.readthedocs.io/en/latest/live-reloading-and-sass-compilation.html









Deployment
----------
