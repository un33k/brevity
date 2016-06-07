from .base.deployable import *

if DJANGO_SERVER_TYPE != 'TEST':
    warnings.warn('Invalid Server Type. ({})'.format(DJANGO_SERVER_TYPE))
    sys.exit(0)

ALLOWED_HOSTS = ["*"]


# Storage
#######################################
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# In-Memory Database
#######################################
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}

# Cache DB. Clean slate before each test
#######################################
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'unittest_db'
    }
}

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
            'level': 'ERROR',
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
        log_level = 'ERROR'
    LOGGING['loggers'].update({
        app: {
            'handlers': ['console'],
            'level': log_level,
        }
    })

# Restful Configuration
#######################################
# REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = (
#     'rest_framework.authentication.BasicAuthentication',
# ) + REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES']

# REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
#     'anon': '50000/hour',
#     'user': '50000/hour',
#     'burst': '50000/min',
#     'sustained': '50000/day',
#     'profile_create': '50000/day',
# }
