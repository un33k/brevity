from .base.deployable import *

DEBUG = False

if DJANGO_SERVER_TYPE != 'PRODUCTION':
    warnings.warn('Invalid Server Type. ({})'.format(DJANGO_SERVER_TYPE))
    sys.exit(0)

if DEPLOYMENT_TYPE != 'PRODUCTION':
    warnings.warn('Invalid Django Seekrets File. {}'.format(DEPLOYMENT_TYPE))
    sys.exit(0)

SITE_EXTRA_CONTEXT_DICT.update({
    'DEBUG': DEBUG,
    'GOOGLE_ADS': True,
})
