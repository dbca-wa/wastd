#!/usr/bin/env python
import os
import sys
import environ

# These lines are required for interoperability between local and container environments.
dot_env = os.path.join(os.getcwd(), '.env')
env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

if os.path.exists(dot_env):
    environ.Env.read_env(dot_env)
else:
    print('manage.py: The .env file does not exist at path {}.'.format(dot_env))


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions on Python 2.
        try:
            import django
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )
        raise
    execute_from_command_line(sys.argv)
