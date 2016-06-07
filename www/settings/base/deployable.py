# Deployable settings -- Not used directly
#########################################
import os
import sys

from .defaults import *
from .social import *
from .menu import *

# Notify the Manifest enabled backend storage to create a unique manifest file.
#######################################
MANIFEST_STATIC_FILE_VERSION = '0.0.106'

# Load up secret files
#######################################
# Site protocol
SITE_PROTOCOL = str(SEEKRETS.get('site_protocol', 'https'))
if SITE_PROTOCOL == 'https':
    SITE_SSL_REDIRECT = str(SEEKRETS.get('site_ssl_redirect', 'NO'))
    if SITE_SSL_REDIRECT == 'YES':
        SECURE_SSL_REDIRECT = True

# Site signature
SECRET_KEY = hmac.new(SEEKRETS['secret_key'].encode(), digestmod=sha1).hexdigest()

DEFAULT_DB_NAME = str(SEEKRETS['database_name'])
DEFAULT_DB_USER = str(SEEKRETS['database_user'])
DEFAULT_DB_PASS = str(SEEKRETS['database_pass'])

# Optional Fields
SITE_SUPERUSER_USERNAME = str(SEEKRETS.get('superuser_username', ''))
SITE_SUPERUSER_EMAIL = str(SEEKRETS.get('superuser_email', ''))
SITE_SUPERUSER_PASSWORD = str(SEEKRETS.get('superuser_password', ''))
SITE_ADMIN_URL_PATH = str(SEEKRETS.get('admin_url_path', 'admino'))

POSTMARK_API_KEY = str(SEEKRETS.get('postmark_api_key', ''))

# Google stuff
SITE_GOOGLE_MAPS = str(SEEKRETS.get('google_maps_key', ''))
SITE_GOOGLE_ANALYTICS = str(SEEKRETS.get('google_analytics_key', 'UA-77109729-1'))
SITE_GOOGLE_AD_CLIENT = str(SEEKRETS.get('google_ad_client', ''))
SITE_GOOGLE_AD_SLOT = str(SEEKRETS.get('google_ad_slot', ''))
ADWARE_DEFAULT_AD_CLIENT = SITE_GOOGLE_AD_CLIENT
ADWARE_DEFAULT_AD_SLOT = SITE_GOOGLE_AD_SLOT

# Site Object
#######################################
SITE_DOMAIN = str(SEEKRETS['site_domain']).lower()
ALLOWED_HOSTS = SEEKRETS.get('allowed_hosts')

# AWS Related
#######################################
AWS_ACCESS_KEY_ID = str(SEEKRETS.get('aws_id', ''))
AWS_SECRET_ACCESS_KEY = str(SEEKRETS.get('aws_secret', ''))
if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
    AWS_S3_SECURE_URLS = False
    AWS_QUERYSTRING_AUTH = False
    AWS_HEADERS = {'Cache-Control': 'max-age=86400', }
    AWS_S3_URL_PROTOCOL = SITE_PROTOCOL + ':'
    AWS_MEDIA_BUCKET_NAME = str(SEEKRETS.get('aws_media_bucket_name', ''))
    AWS_MEDIA_CDN = str(SEEKRETS.get('aws_media_bucket_cname', ''))
    AWS_STATIC_BUCKET_NAME = str(SEEKRETS.get('aws_static_bucket_name', ''))
    AWS_STATIC_CDN = str(SEEKRETS.get('aws_static_bucket_cname', ''))
    AWS_MEDIA_FILE_STORAGE = 'siteware.backends.storages.default.MediaFilesStorage'
    AWS_STATIC_FILES_STORAGE = 'siteware.backends.storages.default.ManifestStaticFilesStorage'
    MEDIA_ASSETS_PREFIX = 'm'
    STATIC_ASSETS_PREFIX = 's'

    # Keep Django into loop regarding our AWS storage backends
    STATICFILES_STORAGE = AWS_STATIC_FILES_STORAGE
    DEFAULT_FILE_STORAGE = AWS_MEDIA_FILE_STORAGE


# Mail Server
#######################################
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
DEFAULT_FROM_EMAIL = str(SEEKRETS.get('default_from_email', 'support@{}'.format(SITE_DOMAIN)))
EMAIL_SUBJECT_PREFIX = '[{}]'.format(SITE_DOMAIN)
# Server error messges are sent by this email
SERVER_EMAIL = str(SEEKRETS.get('default_support_email', DEFAULT_FROM_EMAIL))
# System erros (5XX) are sent to this address
ADMINS = (('Server Admin', '{}'.format(str(SEEKRETS.get('default_admin_email', DEFAULT_FROM_EMAIL)))),)
# Page Not Found (404) errors are sent to this address
MANAGERS = (('Site Admin', '{}'.format(str(SEEKRETS.get('default_manager_email', DEFAULT_FROM_EMAIL)))),)

# Middlewares
#######################################
HEARTBEAT_MIDDLEWARE = ('pulseware.middleware.heartbeat.HeartbeatMiddleWare',)
MIDDLEWARE_CLASSES = HEARTBEAT_MIDDLEWARE + MIDDLEWARE_CLASSES + (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',

    'django_user_agents.middleware.UserAgentMiddleware',
    'profileware.middleware.ForceLogoutMiddleware',

    'auditware.middleware.user.UserAuditMiddleware',
    'auditware.middleware.logout.LogoutEnforcementMiddleware',
    'pulseware.middleware.heartbeat.HeartbeatMiddleWare',
    'userware.middleware.switch.UserSwitchMiddleware',
    'profileware.middleware.RedirectKnownExceptionMiddleware',
    'profileware.middleware.ConvertMessageMiddleware',

    # last resort, keep last
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
)

# Authentication backend
#######################################
AUTHENTICATION_BACKENDS = (
    'social.backends.google.GooglePlusAuth',
    'social.backends.facebook.FacebookOAuth2',
    'userware.backends.ModelBackend',
    'django.contrib.auth.backends.ModelBackend',
)

# Cache Related Stuff
#######################################
CACHES['default'] = CACHES['ProductionRedisCache']

CACHE_MIDDLEWARE_KEY_PREFIX = '{}:'.format(SITE_PROJ_NAME.lower())
CACHE_MIDDLEWARE_SECONDS = 15 * 60

# Sessions
######################################
SESSION_ENGINE_USES_COOKIE = True
if SESSION_ENGINE_USES_COOKIE:
    SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
    SESSION_COOKIE_DOMAIN = '.' + SITE_DOMAIN
    SESSION_COOKIE_HTTPONLY = True
    SESSION_IDLE_TIMEOUT = 60 * 60 * 24
    SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Installed Apps
#######################################
INSTALLED_APPS = INSTALLED_APPS + (

    # Tools, Utils
    'social.apps.django_app.default',
    'pulseware',
    'django_user_agents',
    'autocomplete_light',
    'bootstrap3',
    'storages',
    'taggit',
    'menuware',
    'ipware',
    'userware',
    'auditware',
    'contactware',
    'tracware',

    # User, Accounts
    'profileware',

    # Ads,
    'adware',

    # Content
    'articleware',

    # RestFul
    'rest_framework',
    'rest_framework.authtoken',
    'api_v1',

    'portal',  # in change of this project (aka site)
    'siteware',

    # last application to finalize things
    'finalware',
)

# Account activities
#######################################
LOGIN_URL = '/account/user/login'
LOGIN_REDIRECT_URL = '/'

LOGOUT_URL = '/account/user/logout'
LOGOUT_REDIRECT_URL = '/'

# Custom User
#######################################
AUTH_USER_MODEL = 'profileware.UserProfile'

# Database
#######################################
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

# Site logger level
#######################################
for app in INSTALLED_APPS:
    LOGGING['loggers'].update({
        app: {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        }
    })

# Site objects auto config
#######################################
# site info (you need at least one site)
SITE_OBJECTS_INFO_DICT = {
    '1': {
        'name': SITE_PROJ_NAME,
        'domain': SITE_DOMAIN,
    },
}
SITE_ID = 1

# App specific template directory structure
# #######################################
USERWARE_TEMPLATE_BASE_DIR = os.path.join('admin', 'user')
PROFILEWARE_TEMPLATE_BASE_DIR = os.path.join('admin', 'profile')
ARTICLEWARE_TEMPLATE_BASE_DIR = os.path.join('admin', 'article')
ADWARE_TEMPLATE_BASE_DIR = os.path.join('admin', 'ads')

# Email send using Postmark key
#######################################
EMAIL_BACKEND = 'postmark.django_backend.EmailBackend'
POSTMARK_SENDER = DEFAULT_FROM_EMAIL

# If Session is installed, enable them in admin via the finalware app
# #####################################################################
if 'django.contrib.sessions' in INSTALLED_APPS and 'finalware' in INSTALLED_APPS:
    SITE_ENABLE_SESSION_IN_ADMIN = True

SITE_EXTRA_CONTEXT_DICT = {
    'API_VERSION': '1',
}

# Restful Framework
#######################################
REST_FRAMEWORK = {

    'PAGINATE_BY': 2,
    'MAX_PAGINATE_BY': 2,
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',

    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',

    # allow dynamic pagination size `?page_size=xxx`.
    'PAGINATE_BY_PARAM': 'page_size',

    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),

    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),

    'DEFAULT_MODEL_SERIALIZER_CLASS': (
        'rest_framework.serializers.HyperlinkedModelSerializer',
    ),

    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
        'rest_framework.permissions.DjangoModelPermissions',
        'rest_framework.permissions.IsAdminUser',
    ),

    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.ScopedRateThrottle',
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ),

    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'burst': '60/min',
        'sustained': '1000/day',
        'profile_create': '20/day',
    }
}

SITE_EXTRA_CONTEXT_DICT = {
    "protocol": SITE_PROTOCOL,
    "media_cdn_domain": AWS_MEDIA_CDN.split('//')[1] if AWS_MEDIA_CDN else '',
    "static_cdn_domain": AWS_STATIC_CDN.split('//')[1] if AWS_STATIC_CDN else '',
    "media_cdn_url": getattr(this_file, 'AWS_MEDIA_CDN', ''),
    "static_cdn_url": getattr(this_file, 'AWS_STATIC_CDN', ''),
    "social_auth_enabled": getattr(this_file, 'SOCIAL_AUTH_ENABLED_PROVIDERS', ''),
    "social_fb_app_id": getattr(this_file, 'SOCIAL_AUTH_FACEBOOK_KEY', ''),
    "google_maps_key": SITE_GOOGLE_MAPS,
}

PULSEWARE_DEFAULT_SETTINGS = {
    'PATH': '/site/heartbeat',
    'RETURN_CODE': 503,
    'CACHE_HEALTH': False,
    'DATABASE_READ_HEALTH': True,
    'DATABASE_WRITE_HEALTH': True
}
