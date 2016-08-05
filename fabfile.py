"""Fabric makefile.

Convenience wrapper for often used operations.
"""
from fabric.api import local, env  # settings, cd, run
from fabric.colors import green, yellow  # red
# from fabric.contrib.files import exists, upload_template

env.hosts = ['localhost', ]

def clean():
        """Delete .pyc, temp and swap files."""
        local("./manage.py clean_pyc")
        local("find . -name \*~ -delete")
        local("find . -name \*swp -delete")

def pip():
    """Install python requirements."""
    local("pip install -r requirements/all.txt")


def migrate():
    """Syncdb, update permissions, migrate all apps."""
    local("python manage.py migrate")
    local("python manage.py update_permissions")


def shell():
    """Open a shell_plus."""
    local('python manage.py shell_plus')


def go():
    """Run the app with local settings and runserver (dev)."""
    local('python manage.py collectstatic --noinput && \
           python manage.py runserver --settings=config.settings.local 0.0.0.0:8220')


def pro():
    """Run the app with local settings and runserver (dev)."""
    local('python manage.py collectstatic --noinput && \
           python manage.py runserver --settings=config.settings.production 0.0.0.0:8220')


def pep():
    """Run PEP style compliance audit and write warnings to logs/pepXXX.log."""
    local('pydocstyle > logs/pep257.log', capture=True)
    local('flake8', capture=True)


def test():
    """Run test suite, re-use db."""
    print(yellow("Running tests..."))
    local('coverage run --source="." manage.py test'
          ' --settings=config.settings.test --keepdb -v 2'
          ' && coverage report -m', shell='/bin/bash')
    local('honcho run coveralls')
    print(green("Completed running tests."))
