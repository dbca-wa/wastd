# -*- coding: utf-8 -*-
"""Fabric makefile.

Convenience wrapper for often used operations.
"""
from fabric.api import env, local  # settings, cd, run
from fabric.colors import green, yellow  # red
import confy
from confy import env as confyenv
try:
    confy.read_environment_file(".env")
except:
    pass

# from fabric.contrib.files import exists, upload_template

env.hosts = ['localhost', ]


def clean():
    """Delete .pyc, temp and swap files."""
    local("./manage.py clean_pyc")
    local("find . -name \*~ -delete")
    local("find . -name \*swp -delete")


def pip():
    """Install python requirements."""
    local("pip install -r requirements/base.txt")


def static():
    """Link static files."""
    local("find -L staticfiles/ -type l -delete")
    local("python manage.py collectstatic -v 0 --noinput -l "
          "|| python manage.py collectstatic -v 0 --clear --noinput -l")


def migrate():
    """Syncdb, update permissions, migrate all apps."""
    local("python manage.py migrate")
    local("python manage.py update_permissions")


def deploy():
    """Refresh application. Run after code update.

    Installs dependencies, runs syncdb and migrations, re-links static files.
    """
    pip()
    static()
    migrate()
    clean()


def shell():
    """Open a shell_plus."""
    local('python manage.py shell_plus')

def rundev():
    """Runserver with dev settings."""
    local('python manage.py runserver --settings=config.settings.local 0.0.0.0:8220')


def go():
    """Run the app with development settings and runserver."""
    static()
    rundev()


def pro():
    """Run the app with production settings and runserver."""
    static()
    local('python manage.py runserver --settings=config.settings.production 0.0.0.0:8220')


def wsgi():
    """Serve with uwsgi."""
    static()
    local('uwsgi --http 0.0.0.0:8220 --wsgi-file config/wsgi.py')


def ulous():
    """Serve fabulously with green unicorn."""
    static()
    local('gunicorn config.wsgi --config config/gunicorn.ini')


def pep():
    """Run PEP style compliance audit and write warnings to logs/pepXXX.log."""
    local('pydocstyle > logs/pep257.log', capture=True)


def test():
    """Run test suite."""
    print(yellow("Running tests..."))
    local('COVERAGE_PROCESS_START=./.coveragerc coverage run --parallel-mode '
          '--concurrency=multiprocessing --rcfile=./.coveragerc ' 
          'manage.py test --settings=config.settings.test --parallel 4 --keepdb -v 2 '
          '&& coverage report -m', shell='/bin/bash')
    local('coveralls')
    print(green("Completed running tests."))


def doc():
    """Compile docs, draw data models and transitions."""
    local("mkdir -p docs_source/_static && "
          "cd docs_source && make clean && "
          "make singlehtml && cd ..")

def dbuild():
    """Build Docker image."""
    ver = confyenv("WASTD_RELEASE", default="0.1.0")
    print(yellow("Building docker images with tag latest and {0}...".format(ver)))
    local("rm logs/wastd.log && touch logs/wastd.log")
    local("docker build -t dbcawa/wastd -t dbcawa/wastd:{0} .".format(ver))

def dpush():
    """Push Docker image to Dockerhub. Requires `docker login`."""
    print(yellow("Pushing docker images to DockerHub..."))
    local("docker push dbcawa/wastd")

def docker():
    """Build and push docker images."""
    dbuild()
    dpush()
    ver = confyenv("WASTD_RELEASE", default="0.1.0")
    print(green(
        "Updated Docker images are available on DockerHub "
        "as dbcawa/wastd:latest and dbcawa/wastd:{0}".format(ver)))

def tag():
    """Tag code with WASTD_RELEASE and push to GitHub."""
    ver = confyenv("WASTD_RELEASE", default="0.1.0")
    local("git tag -a {0} -m 'Version {0}'".format(ver))
    local("git push origin {0}".format(ver))
    print(green("Code tagged as {0} and pushed to GitHub.".format(ver)))

def release():
    """Make release: doc, tag, docker."""
    doc()
    tag()
    docker()
