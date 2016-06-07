import os
import uuid
from datetime import datetime

from django.utils.timezone import now
from django.conf import settings

from toolware.utils.generic import get_uuid
from slugify import slugify

from . import defaults as defs


def get_default_username(token=None):
    """
    Returns a default username for user
    """
    if token is None:
        token = '{}'.format(datetime.now().microsecond)
    username = '{}{}'.format(defs.PROFILEWARE_USERNAME_PRFIX,
        str(uuid.uuid5(uuid.NAMESPACE_DNS, token)).split('-')[-1])
    return username.upper()


def get_template_path(name):
    """
    Given a template name, it returns the relative path from the template dir.
    """
    path = os.path.join(defs.PROFILEWARE_TEMPLATE_BASE_DIR, name)
    return path


def uploadto_user_photo(instance, filename):
    """
    Given an image filename, returns a relative path to the image for a member.
    """
    path = 'images/members'
    base, ext = os.path.splitext(filename.lower())
    base = get_uuid(12, 4)
    date = now().strftime("%Y/%m/%d")

    upload_to = '{}/photos/{}/{}{}'.format(path, date, slugify(base), ext)
    return upload_to


def is_social_auth_enabled(request):
    enabled_list = getattr(settings, 'SOCIAL_AUTH_ENABLED_PROVIDERS', [])
    if len(enabled_list) > 0:
        return True
    return False
