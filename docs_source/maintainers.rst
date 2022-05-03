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