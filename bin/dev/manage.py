#!/usr/bin/env python

import os
import sys

from django.core.management import execute_from_command_line

# Ever forgot (DEBUG = True) on your production server? Well no more!
# This is a drop-in replacement of Django's (manage.py) to be used when developing / debugging.
# Never, Ever use it on a production site
################################################################################

# Bootstrap Django
for item in ['api', 'apps', 'www']:
    sys.path.insert(0, os.path.abspath(os.path.join(
        os.path.dirname(__file__), os.pardir, os.pardir, item)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.development')
execute_from_command_line(sys.argv)
