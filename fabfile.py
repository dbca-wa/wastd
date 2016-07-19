"""Fabric makefile.

Convenience wrapper for often used operations.
"""
from fabric.api import local, sudo, settings, env  # cd, run
from fabric.colors import green, yellow  # red
# from fabric.contrib.files import exists, upload_template

env.hosts = ['localhost', ]


def migrate():
    """Syncdb, update permissions, migrate all apps."""
    local("python manage.py migrate")
    local("python manage.py update_permissions")


def go():
    """Run the app with runserver (dev)."""
    local('python manage.py runserver 0.0.0.0:5000')


def test():
    """Write PEP8 warnings to logs/pep8.log and run test suite, re-use db."""
    print(yellow("Running tests..."))
    local('coverage run --source="." manage.py test'
          ' --settings=config.settings.test --keepdb -v 2'
	  ' && coverage report -m', shell='/bin/bash')
    print(green("Completed running tests."))

