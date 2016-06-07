
from . import aws as aws_backend
from . import fs as fs_backend

from ... import defaults as defs

if defs.CLOUD_CDN_ENABLED:
    class MediaFilesStorage(aws_backend.MediaFilesStorage):
        pass

    class StaticFilesStorage(aws_backend.StaticFilesStorage):
        pass

    class ManifestStaticFilesStorage(aws_backend.ManifestStaticFilesStorage):
        pass
else:
    class MediaFilesStorage(fs_backend.MediaFilesStorage):
        pass

    class StaticFilesStorage(fs_backend.StaticFilesStorage):
        pass

    class ManifestStaticFilesStorage(fs_backend.ManifestStaticFilesStorage):
        pass
