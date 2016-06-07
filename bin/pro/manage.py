#!/usr/bin/env python

import os
import sys

from django.core.management import execute_from_command_line

# This is a drop-in replacement of Django's (manage.py) for your production use.
################################################################################

# Bootstrap Django
for item in ['api', 'apps', 'www']:
    sys.path.insert(0, os.path.abspath(os.path.join(
        os.path.dirname(__file__), os.pardir, os.pardir, item)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.production')
execute_from_command_line(sys.argv)
