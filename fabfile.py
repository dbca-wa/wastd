"""Fabric makefile.

Convenience wrapper for often used operations.
"""
from fabric.api import local, env, settings  # cd, run
from fabric.colors import green, yellow  # red
# from fabric.contrib.files import exists, upload_template

env.hosts = ['localhost', ]


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
    local('python manage.py runserver --settings=config.settings.local 0.0.0.0:5000')


def _pep257():
    """Write PEP257 compliance warnings to logs/pep257.log."""
    print(yellow("Writing PEP257 warnings to logs/pep257.log..."))
    with settings(warn_only=True):
        local('pydocstyle --ignore="migrations" > logs/pep257.log',
              capture=True)


def _pep8():
    """Write PEP8 compliance warnings to logs/pep8.log."""
    print(yellow("Writing PEP8 warnings to logs/pep8.log..."))
    with settings(warn_only=True):
        local('flake8 --exclude="migrations" --max-line-length=120 ' +
              '--output-file=logs/pep8.log wastd', capture=True)


def pep():
    """Run PEP style compliance audit and write warnings to logs/pepXXX.log."""
    _pep8()
    _pep257()


def test():
    """Run test suite, re-use db."""
    print(yellow("Running tests..."))
    local('coverage run --source="." manage.py test'
          ' --settings=config.settings.test --keepdb -v 2'
          ' && coverage report -m', shell='/bin/bash')
    print(green("Completed running tests."))
