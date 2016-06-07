from django.conf import settings

MANIFEST_STATIC_FILE_VERSION = getattr(settings, 'MANIFEST_STATIC_FILE_VERSION', '1.1')

CLOUD_CDN_ENABLED = getattr(settings, 'CLOUD_CDN_ENABLED', True)
