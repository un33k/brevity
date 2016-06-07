
from django.core.files.base import ContentFile
from django.utils.translation import ugettext_lazy as _

from requests import request
from requests import HTTPError

from social.backends.google import GooglePlusAuth
from social.backends.facebook import FacebookOAuth2
from social.exceptions import AuthException
from social.pipeline.user import get_username

from .models import UserProfile
from . import utils as util


def get_unique_username(strategy, details, user=None, *args, **kwargs):
    """
    Handle username collision.
    """
    received_username = get_username(strategy, details, user, *args, **kwargs)
    username = received_username.get('username')
    if username:
        count = 0
        while count < 20:
            try:
                user = UserProfile.objects.get(username=username)
            except UserProfile.DoesNotExist:
                return {'username': username}
            count += 1
            username = '{}{}'.format(username, count)
    return {'username': util.get_default_username()}


def associate_by_email(backend, details, user=None, *args, **kwargs):
    """
    Associate current auth with a user with the same email address in the DB.

    This pipeline entry is not 100% secure unless you know that the providers
    enabled enforce email verification on their side.
    """
    if user:
        return None

    email = details.get('email')
    if email:
        # Try to associate accounts registered with the same email address,
        # only if it's a single object. AuthException is raised if multiple
        # objects are returned.
        users = list(backend.strategy.storage.user.get_users_by_email(email))
        if len(users) == 0:
            return None
        elif len(users) > 1:
            raise AuthException(backend,
                _('The given email address is associated with another account.'))
        else:
            return {'user': users[0]}
    else:
        raise AuthException(backend, _('Unable to retrieve a verified email.'))


def save_photo(backend, user, response, details, is_new=False, *args, **kwargs):
    """
    Add photo to profile if exists.
    """
    if not user.photo:
        url = None
        if isinstance(backend, GooglePlusAuth):
            if response.get('image') and response['image'].get('url'):
                url = response['image'].get('url')
                params = {'sz': '512'}
        elif isinstance(backend, FacebookOAuth2):
            url = "https://graph.facebook.com/{}/picture".format(response['id'])
            params = {'type': 'large'}
        if url:
            try:
                response = request('GET', url, params=params)
                response.raise_for_status()
            except HTTPError:
                pass
            else:
                image = '{}_photo.jpg'.format(user.username)
                user.photo.save(image, ContentFile(response.content))
                user.save()
