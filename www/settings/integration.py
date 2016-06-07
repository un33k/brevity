from .base.deployable import *

if DJANGO_SERVER_TYPE != 'INTEGRATION':
    warnings.warn('Invalid Server Type. ({})'.format(DJANGO_SERVER_TYPE))
    sys.exit(0)

if DEPLOYMENT_TYPE != 'INTEGRATION':
    warnings.warn('Invalid Django Seekrets File. {}'.format(DEPLOYMENT_TYPE))
    sys.exit(0)

DEBUG = False
DEBUG_TEMPLATE = False

SITE_GOOGLE_ANALYTICS = ''
SITE_EXTRA_CONTEXT_DICT.update({
    'DEBUG': DEBUG,
    'GOOGLE_ADS': False,
})

# Site Objects
#######################################
INTEGRATION_SITE_DOMAIN_NAME = str(SEEKRETS['site_domain']).lower()
ALLOWED_HOSTS += [INTEGRATION_SITE_DOMAIN_NAME, ]

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

# Site objects auto config
#######################################
# site info (you need at least one site)
SITE_OBJECTS_INFO_DICT = {
    '1': {
        'name': SITE_PROJ_NAME + ' - Integration',
        'domain': SITE_DOMAIN,
    },
}
SITE_ID = 1

SECURE_SSL_REDIRECT = False

if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
    CLOUD_CDN_ENABLED = True
    SITE_PROTOCOL = 'http'
    AWS_MEDIA_BUCKET_NAME = str(SEEKRETS.get('aws_integration_bucket_name', ''))
    AWS_MEDIA_CDN = str(SEEKRETS.get('aws_integration_bucket_cname', ''))
    AWS_STATIC_BUCKET_NAME = AWS_MEDIA_BUCKET_NAME
    AWS_STATIC_CDN = AWS_MEDIA_CDN
    AWS_S3_URL_PROTOCOL = SITE_PROTOCOL + ':'
