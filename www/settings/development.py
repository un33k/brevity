import os

from .base.deployable import *

if DJANGO_SERVER_TYPE != 'DEVELOPMENT':
    warnings.warn('Invalid Django Server Type. {}'.format(DJANGO_SERVER_TYPE))
    sys.exit(0)

if DEPLOYMENT_TYPE != 'DEVELOPMENT':
    warnings.warn('Invalid Django Seekrets File. {}'.format(DEPLOYMENT_TYPE))
    sys.exit(0)

MIDDLEWARE_CLASSES = list(MIDDLEWARE_CLASSES)
INSTALLED_APPS = list(INSTALLED_APPS)
TEMPLATES = list(TEMPLATES)

# Debug info
#######################################
DEBUG = True
DEBUG_TEMPLATE = DEBUG

DEBUG_AWS = False
DEBUG_USE_SQLITE3 = True
DEBUG_SECURIFY_URLS = True
DEBUG_SKIP_CSRF_MIDDLEWARE = True
DEBUG_SKIP_CLICKJACKING_MIDDLEWARE = True
DEBUG_ENABLE_TOOLBAR = False
DEBUG_ENABLE_COMMAND_EXTENSSION = True
DEBUG_LOGGING_ONLY = True
DEBUG_CONSOLE_LOG_LEVEL = 'DEBUG'
DEBUG_ENABLE_LOCAL_CACHE_BACKEND = True
DEBUG_USE_LOCAL_SMTP = False
DEV_IP_ADDRESS = '127.0.0.1'

SECURE_SSL_REDIRECT = False
CLOUD_CDN_ENABLED = False

SITE_GOOGLE_ANALYTICS = ''
SITE_EXTRA_CONTEXT_DICT.update({
    'DEBUG': DEBUG,
    'GOOGLE_ADS': False,
})

# Context processor
#######################################
TEMPLATES[0]['OPTIONS']['context_processors'].append(
    'django.core.context_processors.debug',
)
TEMPLATES[0]['APP_DIRS'] = True
del TEMPLATES[0]['OPTIONS']['loaders']

if DEBUG_TEMPLATE:
    TEMPLATES[0]['OPTIONS']['debug'] = True

# quick test of project with sqlite3
#######################################
if DEBUG_USE_SQLITE3:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.abspath(os.path.join(PROJ_ROOT_DIR, SITE_PROJ_NAME.lower() + '_db')),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': DEFAULT_DB_NAME,
            'USER': DEFAULT_DB_USER,
            'PASSWORD': DEFAULT_DB_PASS,
            # 'HOST':     ',
            # 'PORT':     ',
        }
    }

# remove CSRF if flag is set
#######################################
if DEBUG_SKIP_CSRF_MIDDLEWARE:
    del MIDDLEWARE_CLASSES[MIDDLEWARE_CLASSES.index('django.middleware.csrf.CsrfViewMiddleware')]

# remove ClickJacking if flag is set
#######################################
if DEBUG_SKIP_CLICKJACKING_MIDDLEWARE:
    del MIDDLEWARE_CLASSES[MIDDLEWARE_CLASSES.index('django.middleware.clickjacking.XFrameOptionsMiddleware')]

# debug toolbar
#######################################
if DEBUG_ENABLE_TOOLBAR and DEBUG:
    # bless debug toolbar with development (ONLY) IP(s)
    INTERNAL_IPS = DEV_IP_ADDRESS
    try:
        import debug_toolbar
    except ImportError:
        pass
    else:
        # order matters, so insert the debug toolbar app right after the common middleware
        common_index = MIDDLEWARE_CLASSES.index('django.middleware.common.CommonMiddleware')
        MIDDLEWARE_CLASSES.insert(common_index + 1, 'debug_toolbar.middleware.DebugToolbarMiddleware')
        INSTALLED_APPS.append('debug_toolbar')
        DEBUG_TOOLBAR_CONFIG = {
            'SHOW_TOOLBAR_CALLBACK': lambda req: True,
            'INTERCEPT_REDIRECTS': False,
        }


# debug command extensions (lot of goodies)
#######################################
if DEBUG_ENABLE_COMMAND_EXTENSSION:
    try:
        import django_extensions
    except ImportError:
        pass
    else:
        INSTALLED_APPS.append('django_extensions')

# use dev server instead of the built-in dev server
#######################################
# INSTALLED_APPS.append('devserver')
# DEVSERVER_DEFAULT_ADDR = DEV_IP_ADDRESS
# DEVSERVER_DEFAULT_PORT = 8080

# debug logging
#######################################
if DEBUG_LOGGING_ONLY:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'simple': {'format': '[%(name)s] %(levelname)s: [%(lineno)d] %(message)s'},
            'full': {'format': '%(asctime)s [%(name)s] %(levelname)s: [%(lineno)d] %(message)s'}
        },
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse'
            }
        },
        'handlers': {
            'mail_admins': {
                'level': 'DEBUG',
                'filters': ['require_debug_false'],
                'class': 'django.utils.log.AdminEmailHandler'
            },
            'console': {
                'level': '{}'.format(DEBUG_CONSOLE_LOG_LEVEL),
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
            },
        },
        'loggers': {
            'django.request': {
                'handlers': ['console'],
                'level': 'DEBUG',
            },
        }
    }

# Site logger level
#######################################
for app in INSTALLED_APPS:
    log_level = 'ERROR'
    if not app.startswith('django'):
        log_level = 'DEBUG' if DEBUG else 'ERROR'
    LOGGING['loggers'].update({
        app: {
            'handlers': ['console'],
            'level': log_level,
        }
    })

# cache backend during debugging
#######################################
CACHES['default'] = CACHES['FakeCache']
if DEBUG_ENABLE_LOCAL_CACHE_BACKEND:
    CACHES['default'] = CACHES['DevelopmentCache']

# Don't care about this in debug mode (allows login via admin in debug when session in cookies used)
#######################################
SESSION_COOKIE_DOMAIN = ''

# Assets overwrite
#######################################
if DEBUG_AWS:
    CLOUD_CDN_ENABLED = True
    DEBUG = False
    SITE_PROTOCOL = 'https'
    AWS_MEDIA_BUCKET_NAME = str(SEEKRETS.get('aws_staging_bucket_name', ''))
    AWS_MEDIA_CDN = str(SEEKRETS.get('aws_staging_bucket_cname', ''))
    AWS_STATIC_BUCKET_NAME = AWS_MEDIA_BUCKET_NAME
    AWS_STATIC_CDN = AWS_MEDIA_CDN
    AWS_S3_URL_PROTOCOL = SITE_PROTOCOL + ':'
else:
    DEFAULT_FILE_STORAGE = 'siteware.backends.storages.default.MediaFilesStorage'
    STATICFILES_STORAGE = 'siteware.backends.storages.default.StaticFilesStorage'
    # Path to the static directory (collectstatic copies static assets to for deployment)
    STATIC_ROOT = os.path.abspath(os.path.join(ASSETS_DIR, 'collect'))
    # Path to the dynamic directory for user uploaded data
    MEDIA_ROOT = os.path.abspath(os.path.join(ASSETS_DIR, 'upload'))
    # URL to the static assets
    STATIC_URL = '/s/'
    # URL to the user uploaded assets
    MEDIA_URL = '/m/'
    SITE_PROTOCOL = 'http'

# Falls on development IP from finalize.sites
#######################################
SITE_OBJECTS_INFO_DICT['2'] = {
    'name': SITE_PROJ_NAME + ' - Development',
    'domain': '{}:8080'.format(DEV_IP_ADDRESS)
}
SITE_ID = 2

# Admin User Overwrite (warning: not to be used in production)
#######################################
SITE_SUPERUSER_PASSWORD = 'hello'

# Email send using Postmark key
#######################################
if DEBUG_USE_LOCAL_SMTP:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Swagger interface
#######################################
if 'rest_framework' in INSTALLED_APPS:

    # Restful Configuration
    #######################################
    REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = (
        'rest_framework.authentication.BasicAuthentication',
    ) + REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES']

    REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
        'anon': '50000/hour',
        'user': '50000/hour',
        'burst': '50000/min',
        'sustained': '50000/day',
        'profile_create': '50000/day',
    }

    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = (
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework.renderers.AdminRenderer',
    ) + REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES']

    # Swagger Restful Configuration
    #######################################
    if 'rest_framework_swagger' not in INSTALLED_APPS:
        rest_index = INSTALLED_APPS.index('rest_framework')
        INSTALLED_APPS.insert(rest_index + 1, 'rest_framework_swagger')

    # SWAGGER_SETTINGS = {
    #     'exclude_namespaces': [],
    #     'api_version': '1',
    #     'api_path': '/',
    #     'api_key': 'un33k',
    #     'enabled_methods': ['get', 'post', 'put', 'patch', 'delete'],
    #     'is_authenticated': False,
    #     'is_superuser': False
    # }
