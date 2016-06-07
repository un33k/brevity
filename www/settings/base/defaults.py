# Bootstrap settings - Not used directly
#########################################
import os
import sys
import re
import warnings
import uuid
import hmac
from hashlib import sha1

from .seekrets import *


DJANGO_SERVER_TYPE = os.environ.get('DJANGO_SERVER_TYPE', 'UNKNOWN')

# Domain / Project Name
#######################################
SITE_PROJ_NAME = str(SEEKRETS.get('site_name', 'Brevity'))

# Site Specific Info  What does your site do?
# #######################################
SITE_NAME = SITE_ORGANIZATION = SITE_PROJ_NAME
SITE_TITLE = str(SEEKRETS.get('site_title', 'Brevity Publishing'))
SITE_KEYWORDS = str(SEEKRETS.get('site_keyword', 'Brevity, BrevityPress, Blog, Article'))
SITE_DESCRIPTION = str(SEEKRETS.get('site_description',
    'A Powerful Multimedia-Rich Software that aims at making online publishing very simple.'))

# Assets configs
#######################################
ASSETS_DIR = os.path.abspath(os.path.join(PROJ_ROOT_DIR, 'assets'))
# Static directories to look at during the development
STATICFILES_DIRS = ['{}'.format(os.path.abspath(os.path.join(ASSETS_DIR, 'static'))), ]
# Path to the static directory (collectstatic copies static assets to for deployment)
STATIC_ROOT = os.path.abspath(os.path.join(ASSETS_DIR, 'collect'))
# Path to the dynamic directory for user uploaded data
MEDIA_ROOT = os.path.abspath(os.path.join(ASSETS_DIR, 'upload'))
# URL to the static assets
STATIC_URL = '/s/'
# URL to the user uploaded assets
MEDIA_URL = '/m/'

# Storage
#######################################
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Site Specifics
#######################################
LANGUAGE_CODE = 'en-us'
USE_I18N = False
USE_L10N = False
USE_TZ = True
SITE_PROTOCOL = 'https'
ROOT_URLCONF = 'urls'
DEFAULT_COUNTRY = 'Canada'
TIME_ZONE = 'Canada/Eastern'
APPEND_SLASH = False
USE_THOUSAND_SEPARATOR = True

# Default static file finders in order of precedence
#######################################
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder', (Don't use with remote FS. etc. AWS)
)

# Default Django Applications
#######################################
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'django.contrib.humanize',
    'django.contrib.sitemaps',
    'django.contrib.redirects',
)

# Default Django Middlewares
#######################################
MIDDLEWARE_CLASSES = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
)

# Authentication backend
#######################################
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

# Cache Related
#######################################
CACHES = {
    'DevelopmentCache': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake'
    },
    'ProductionMemcachedCache': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': 'cache-host:11211',
        'TIMEOUT': 180,
        'OPTIONS': {
            'MAX_ENTRIES': 4000,
            'CULL_FREQUENCY': 3,
        }
    },
    'ProductionRedisCache': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://cache-host:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_TIMEOUT': 2,
            'SOCKET_CONNECT_TIMEOUT': 2,
            'IGNORE_EXCEPTIONS': True,
            'TIMEOUT': 5,
        }
    },
    'FakeCache': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Database Related
#######################################
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.abspath(os.path.join(PROJ_ROOT_DIR, SITE_PROJ_NAME.lower() + '_db')),
    }
}

# Template Related
#######################################
TEMPLATES_BASE_DIR = os.path.abspath(os.path.join(PROJ_ROOT_DIR, 'www', 'templates'))
TEMPLATES_SUB_DIRS = [
    'django',    # Django admin overwrites
    'server',    # HTTP server specific files
    'layout',    # Site layout
    'bs/int',    # Bootstrap templates for internal apps
    'bs/ext',    # Bootstrap templates for external apps
    'md/int',    # Material Design templates for internal apps
    'md/ext',    # Material Design templates for external apps
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # 'APP_DIRS': True,
        'DIRS': [
            '{}'.format(os.path.join(TEMPLATES_BASE_DIR, _dir)) for _dir in TEMPLATES_SUB_DIRS
        ],
        'OPTIONS': {
            'context_processors': [
                'django.core.context_processors.csrf',
                'django.contrib.auth.context_processors.auth',
                'django.core.context_processors.i18n',
                'django.core.context_processors.media',
                'django.core.context_processors.static',
                'django.core.context_processors.request',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'social.apps.django_app.context_processors.backends',
                'social.apps.django_app.context_processors.login_redirect',
                'siteware.context_processors.contextify',
                'finalware.context_processors.contextify',
            ],
            'builtins': [
                'django.templatetags.cache',
                'django.templatetags.future',
                'django.templatetags.i18n',
                'django.templatetags.l10n',
                'django.contrib.staticfiles.templatetags.staticfiles',
                'django.templatetags.tz',
                'django.contrib.humanize.templatetags.humanize',

                'menuware.templatetags.menuware',
                'bootstrap3.templatetags.bootstrap3',
                # 'toolware.templatetags.forms',
                'toolware.templatetags.generic',
                'toolware.templatetags.highlight',
                'toolware.templatetags.rounder',
                'toolware.templatetags.strings',
                'toolware.templatetags.variable',
                'articleware.templatetags.track',
                'articleware.templatetags.content',
                'articleware.templatetags.permissions',
                'profileware.templatetags.profile',
                'tracware.templatetags.track',
                'adware.templatetags.adsense',
                'portal.templatetags.search',
                'portal.templatetags.media',
                'portal.templatetags.social',
                'portal.templatetags.track',
            ],
            'loaders': (
                (
                    'django.template.loaders.cached.Loader',
                    (
                        'django.template.loaders.filesystem.Loader',
                        'django.template.loaders.app_directories.Loader',
                    )
                ),
            ),
        },
    },
]

# Broken Link emails: Ignore few request by robots
#######################################
SEND_BROKEN_LINK_EMAILS = False
if SEND_BROKEN_LINK_EMAILS:
    IGNORABLE_404_URLS = (
        re.compile(r'\.(php|cgi|asp|css|js|aspx)'),
        re.compile(r'^/phpmyadmin/'),
        re.compile(r'^/beta/'),
        re.compile(r'^/favicon\.ico$'),
        re.compile(r'^/robots\.txt$'),
    )

# Basic logging
#######################################
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'simple': {
            'format': '[%(name)s] %(levelname)s: [%(lineno)d] %(message)s',
        },
        'full': {
            'format': '%(asctime)s [%(name)s] %(levelname)s: [%(lineno)d] %(message)s',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': [
                'require_debug_false',
            ],
            'class': 'django.utils.log.AdminEmailHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# Default Django test runner
################################################
TEST_RUNNER = 'django.test.runner.DiscoverRunner'
