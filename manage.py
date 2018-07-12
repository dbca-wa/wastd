#!/usr/bin/env python
import os
import sys

try:
    import confy
    confy.read_environment_file()
except:
    pass

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
