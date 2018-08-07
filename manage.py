#!/usr/bin/env python
"""manage.py for Django app."""
import confy
import os
import sys

# These lines are required for interoperability between local and container environments.
dot_env = os.path.join(os.getcwd(), '.env')
if os.path.exists(dot_env):
    confy.read_environment_file()


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
