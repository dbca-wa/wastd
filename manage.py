#!/usr/bin/env python
"""manage.py for Django app."""
import os
import sys
import confy

confy.read_environment_file()

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
