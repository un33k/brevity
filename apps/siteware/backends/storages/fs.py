from django.conf import settings

from django.core.files.storage import FileSystemStorage as DjangoFileSystemStorage
from django.contrib.staticfiles.storage import StaticFilesStorage as DjangoStaticFilesStorage
from django.contrib.staticfiles.storage import ManifestStaticFilesStorage as DjangoManifestStaticFilesStorage

from ... import defaults as defs
from ... import utils as util


class MediaFilesStorage(DjangoFileSystemStorage):
    """
    Custom storage for uploaded assets. (any file type)
    """
    def __init__(self, *args, **kwargs):
        super(MediaFilesStorage, self).__init__(*args, **kwargs)


class StaticFilesStorage(DjangoStaticFilesStorage):
    """
    Custom storage for static assets. (any file type)
    """
    def __init__(self, *args, **kwargs):
        super(StaticFilesStorage, self).__init__(*args, **kwargs)


class ManifestStaticFilesStorage(DjangoManifestStaticFilesStorage):
    """
    Custom storage for manifest static assets. (any file type).
    Not to be used in development.
    """
    def __init__(self, *args, **kwargs):
        super(ManifestStaticFilesStorage, self).__init__(*args, **kwargs)

    @property
    def manifest_name(self):
        filename = 'staticfiles-{}.json'.format(defs.MANIFEST_STATIC_FILE_VERSION)
        return filename
